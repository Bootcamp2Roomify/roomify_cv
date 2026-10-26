import hmac
import ipaddress
import os
import socket
from urllib.parse import urlparse
import logging
from io import BytesIO

import httpx
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile, Form
from PIL import Image, UnidentifiedImageError
from app.detector import detect_furniture, analyze_image
from app.schemas import DetectionResponse, AnalyzeResponse

logger = logging.getLogger(__name__)

app = FastAPI(title="Roomify CV Service")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg"}
# When set, detection endpoints need "Authorization: Bearer <token>" (for a publicly reachable deployment).
API_TOKEN = os.getenv("CV_API_TOKEN", "")

def require_token(authorization: str | None = Header(None)) -> None:
    if API_TOKEN and not hmac.compare_digest(authorization or "", f"Bearer {API_TOKEN}"):
        raise HTTPException(status_code=401, detail="Missing or invalid token.")

def ensure_public_url(image_url: str) -> None:
    """Rejects URLs that could reach internal services (SSRF), e.g. cloud metadata or localhost."""
    parsed = urlparse(image_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise HTTPException(status_code=400, detail="Image URL must be an http(s) URL.")
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(parsed.hostname, parsed.port or 443)}
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="Unable to load image from URL.")
    for address in addresses:
        ip = ipaddress.ip_address(address.split("%")[0])
        if not ip.is_global:
            raise HTTPException(status_code=400, detail="Image URL must point to a public address.")


async def load_image_from_url(image_url: str) -> Image.Image:
    ensure_public_url(image_url)
    try:
        # Redirects are not followed: they could lead to an address that was never checked.
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            response = await client.get(image_url)
            response.raise_for_status()

        content_type = response.headers.get("content-type", "").split(";")[0]

        if content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail="URL must point to a JPG, JPEG, or PNG image.",
            )

        return Image.open(BytesIO(response.content)).convert("RGB")

    except HTTPException:
        raise
    except (httpx.HTTPError, UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Unable to load image from URL.",
        )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/detect", response_model = DetectionResponse, dependencies=[Depends(require_token)])
async def detect(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG, JPEG, and PNG images are supported.")
    try:
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="Invalid image file.")
    
    return detect_furniture(image)

@app.post("/v1/analyze", response_model=AnalyzeResponse, dependencies=[Depends(require_token)])
async def analyze(
            file: UploadFile | None = File(None),
            image_url: str | None = Form(None),):
    if bool(file) == bool(image_url):
        raise HTTPException(
            status_code=400,
            detail="Provide exactly one of file or image_url.",
        )

    if file:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, JPEG, and PNG images are supported.",
            )

        try:
            image_bytes = await file.read()
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
        except (UnidentifiedImageError, OSError):
            raise HTTPException(status_code=400, detail="Invalid image file.")

    else:
        image = await load_image_from_url(image_url)

    try:
        return analyze_image(image)
    except Exception:
        logger.exception("Furniture analysis failed")
        raise HTTPException(status_code=500, detail="Image analysis failed.")