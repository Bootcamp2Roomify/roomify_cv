from PIL import Image, ImageDraw
from ultralytics import YOLO
from app.schemas import Detection, DetectionResponse

MODEL = YOLO("yolo11n.pt")

TARGET_CLASSES = {
    "bed",
    "chair",
    "dining table",
    "couch",
    "tv",
    "potted plant",
}

LABEL_MAP = {
    "dining table": "table",
    "couch": "sofa",
    "potted plant": "plant",
}

def detect_furniture(image: Image.Image) -> DetectionResponse:
    results = MODEL.predict(image, conf=0.25, verbose=False)
    objects = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            class_name = result.names[class_id]

            if class_name not in TARGET_CLASSES:
                continue

            label = LABEL_MAP.get(class_name, class_name)
            confidence = float(box.conf[0].item())
            bbox = box.xyxy[0].tolist()

            objects.append(
                Detection(
                    label=label,
                    confidence=round(confidence, 4),
                    bbox=[round(value, 2) for value in bbox],
                )
            )
    return DetectionResponse(objects=objects)

def draw_detections(image: Image.Image, detections: DetectionResponse) -> Image.Image:
    debug_image = image.copy()
    draw = ImageDraw.Draw(debug_image)
    
    for detection in detections.objects:
        x1,y1,x2,y2 = detection.bbox
        draw.rectangle([x1,y1,x2,y2], outline="purple", width = 2)
        draw.text(
            (x1, max(0, y1-15)),
            f"{detection.label} {detection.confidence: .2f}",
            fill = "purple",
        )
    return debug_image