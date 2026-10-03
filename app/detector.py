import os
import time
from PIL import Image, ImageDraw
from ultralytics import YOLO
from app.schemas import Detection, DetectionResponse,  AnalyzeObject, NormalizedBBox, AnalyzeResponse

MODEL = YOLO("yolo11n.pt")
MODEL_VERSION = "yolo11n"
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))

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

def get_roomify_label(class_name: str) -> str | None:
    if class_name not in TARGET_CLASSES:
        return None
    return LABEL_MAP.get(class_name, class_name)

def detect_furniture(image: Image.Image) -> DetectionResponse:
    results = MODEL.predict(image, conf=CONFIDENCE_THRESHOLD, verbose=False)
    objects = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            class_name = result.names[class_id]

            label = get_roomify_label(class_name)

            if label is None:
                continue
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

def normalize_bbox(bbox, image_width, image_height):
    x_min, y_min, x_max, y_max = bbox
    return {
        "x": x_min / image_width,
        "y": y_min / image_height,
        "w": (x_max - x_min) / image_width,
        "h": (y_max - y_min) / image_height,
    }
    
def analyze_furniture(image: Image.Image) -> list[AnalyzeObject]:
    results = MODEL.predict(image, conf=CONFIDENCE_THRESHOLD, verbose=False)
    objects = []
    image_width, image_height = image.size

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            class_name = result.names[class_id]

            label = get_roomify_label(class_name)

            if label is None:
                continue
            confidence = float(box.conf[0].item())
            pixel_bbox = box.xyxy[0].tolist()
            normalized = normalize_bbox(pixel_bbox, image_width, image_height)

            objects.append(
                AnalyzeObject(
                    label=label,
                    confidence=round(confidence, 4),
                    bbox=NormalizedBBox(
                        x=round(normalized["x"], 4),
                        y=round(normalized["y"], 4),
                        w=round(normalized["w"], 4),
                        h=round(normalized["h"], 4),
                    ),
                )
            )

    return objects

def analyze_image(image: Image.Image) -> AnalyzeResponse:
    start_time = time.perf_counter()

    objects = analyze_furniture(image)

    processing_time_ms = (time.perf_counter() - start_time) * 1000

    return AnalyzeResponse(
        modelVersion=MODEL_VERSION,
        processingTimeMs=round(processing_time_ms, 2),
        objects=objects,
    )