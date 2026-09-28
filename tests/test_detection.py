from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

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