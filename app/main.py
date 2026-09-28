from io import BytesIO
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from app.detector import detect_furniture
from app.schemas import DetectionResponse


app = FastAPI(title="Roomify CV Service")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/detect", response_model = DetectionResponse)
async def detect(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG, JPEG, and PNG images are supported.")
    try:
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="Invalid image file.")
    
    return detect_furniture(image)