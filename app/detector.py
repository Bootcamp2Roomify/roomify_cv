import os
import time
from PIL import Image, ImageDraw
from app.schemas import Detection, DetectionResponse,  AnalyzeObject, NormalizedBBox, AnalyzeResponse

# MODEL_PATH is a local weights file; ultralytics downloads the named default on first use.
# A .onnx file runs on ONNX Runtime alone (no torch), for hosts with little memory.
MODEL_PATH = os.getenv("MODEL_PATH", "yolo11n.pt")
if MODEL_PATH.endswith(".onnx"):
    from app.onnx_yolo import OnnxYolo
    MODEL = OnnxYolo(MODEL_PATH)
else:
    from ultralytics import YOLO
    MODEL = YOLO(MODEL_PATH)
MODEL_VERSION = os.path.splitext(os.path.basename(MODEL_PATH))[0]
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

def predict_boxes(image: Image.Image) -> list[tuple[str, float, list[float]]]:
    """Runs the model: (Roomify label, confidence, [x1, y1, x2, y2] in pixels) per kept object."""
    if MODEL_PATH.endswith(".onnx"):
        raw = MODEL.predict(image, conf=CONFIDENCE_THRESHOLD)
    else:
        raw = [
            (result.names[int(box.cls[0].item())], float(box.conf[0].item()), box.xyxy[0].tolist())
            for result in MODEL.predict(image, conf=CONFIDENCE_THRESHOLD, verbose=False)
            for box in result.boxes
        ]
    boxes = []
    for class_name, confidence, bbox in raw:
        label = get_roomify_label(class_name)
        if label is not None:
            boxes.append((label, confidence, bbox))
    return boxes

def detect_furniture(image: Image.Image) -> DetectionResponse:
    objects = [
        Detection(
            label=label,
            confidence=round(confidence, 4),
            bbox=[round(value, 2) for value in bbox],
        )
        for label, confidence, bbox in predict_boxes(image)
    ]
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
    objects = []
    image_width, image_height = image.size

    for label, confidence, pixel_bbox in predict_boxes(image):
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