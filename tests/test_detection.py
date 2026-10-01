from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.detector import get_roomify_label, normalize_bbox
from app.schemas import AnalyzeObject, AnalyzeResponse, NormalizedBBox

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_detect_sample_image():
    with open("samples/room.jpeg", "rb") as image:
        response = client.post(
            "/detect",
            files={"file": ("room.jpeg", image, "image/jpeg")},
        )

    assert response.status_code == 200
    data = response.json()
    assert "objects" in data
    assert isinstance(data["objects"], list)

    for obj in data["objects"]:
        assert "label" in obj
        assert "confidence" in obj
        assert "bbox" in obj
        assert len(obj["bbox"]) == 4

def test_no_detection_image():
    image = Image.new("RGB", (640, 640), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.post(
        "/detect",
        files={"file": ("blank.png", buffer, "image/png")},
    )

    assert response.status_code == 200
    assert response.json() == {"objects": []}

def test_invalid_file_type():
    response = client.post(
        "/detect",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400

def test_normalize_bbox():
    bbox = normalize_bbox(
        [100, 50, 500, 250],
        image_width=1000,
        image_height=500,
    )

    assert bbox == {
        "x": 0.1,
        "y": 0.1,
        "w": 0.4,
        "h": 0.4,
    }

def test_category_filtering():
    assert get_roomify_label("chair") == "chair"
    assert get_roomify_label("dining table") == "table"
    assert get_roomify_label("couch") == "sofa"
    assert get_roomify_label("potted plant") == "plant"
    assert get_roomify_label("person") is None
    assert get_roomify_label("bottle") is None

def test_analyze_response_contract(monkeypatch):
    def fake_analyze_image(image):
        return AnalyzeResponse(
            modelVersion="yolo11n",
            processingTimeMs=25.5,
            objects=[
                AnalyzeObject(
                    label="chair",
                    confidence=0.83,
                    bbox=NormalizedBBox(
                        x=0.42,
                        y=0.31,
                        w=0.18,
                        h=0.35,
                    ),
                )
            ],
        )

    monkeypatch.setattr("app.main.analyze_image", fake_analyze_image)

    image = Image.new("RGB", (100, 100), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.post(
        "/v1/analyze",
        files={"file": ("test.png", buffer, "image/png")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "modelVersion": "yolo11n",
        "processingTimeMs": 25.5,
        "objects": [
            {
                "label": "chair",
                "confidence": 0.83,
                "bbox": {
                    "x": 0.42,
                    "y": 0.31,
                    "w": 0.18,
                    "h": 0.35,
                },
            }
        ],
    }

def test_analyze_without_input():
    response = client.post("/v1/analyze")

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Provide exactly one of file or image_url."
    }

def test_analyze_invalid_file_type():
    response = client.post(
        "/v1/analyze",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400

def test_analyze_file_and_url_rejected():
    image = Image.new("RGB", (100, 100), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.post(
        "/v1/analyze",
        files={"file": ("test.png", buffer, "image/png")},
        data={"image_url": "http://example.com/image.png"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Provide exactly one of file or image_url."
    }

def test_analyze_image_url(monkeypatch):
    async def fake_load_image_from_url(image_url):
        return Image.new("RGB", (100, 100), "white")

    def fake_analyze_image(image):
        return AnalyzeResponse(
            modelVersion="yolo11n",
            processingTimeMs=10.0,
            objects=[],
        )

    monkeypatch.setattr(
        "app.main.load_image_from_url",
        fake_load_image_from_url,
    )
    monkeypatch.setattr(
        "app.main.analyze_image",
        fake_analyze_image,
    )

    response = client.post(
        "/v1/analyze",
        data={"image_url": "https://example.com/room.jpeg"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "modelVersion": "yolo11n",
        "processingTimeMs": 10.0,
        "objects": [],
    }

def test_analyze_runtime_failure_returns_500(monkeypatch):
    def fake_analyze_image(image):
        raise RuntimeError("Model crashed")

    monkeypatch.setattr(
        "app.main.analyze_image",
        fake_analyze_image,
    )

    image = Image.new("RGB", (100, 100), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.post(
        "/v1/analyze",
        files={"file": ("test.png", buffer, "image/png")},
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Image analysis failed."
    }