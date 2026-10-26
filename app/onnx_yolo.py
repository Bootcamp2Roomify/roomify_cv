"""YOLO11 inference on ONNX Runtime alone (no torch), so the service fits small free hosts.

Mirrors ultralytics' predict pipeline: centred letterbox to the exported size (pad 114),
class-aware NMS at IoU 0.7, max 300 boxes, boxes scaled back to the original image.
"""
import ast

import numpy as np
import onnxruntime as ort
from PIL import Image

IOU_THRESHOLD = 0.7
MAX_DETECTIONS = 300
CLASS_OFFSET = 7680  # ultralytics' max_wh: shifts boxes per class so NMS never mixes classes


class OnnxYolo:
    def __init__(self, path: str):
        self.session = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
        meta = self.session.get_modelmeta().custom_metadata_map
        self.names: dict[int, str] = ast.literal_eval(meta["names"])
        self.height, self.width = ast.literal_eval(meta["imgsz"])
        self.input_name = self.session.get_inputs()[0].name

    def _letterbox(self, image: Image.Image) -> tuple[np.ndarray, float, float, float]:
        w, h = image.size
        gain = min(self.height / h, self.width / w)
        new_w, new_h = round(w * gain), round(h * gain)
        left = round((self.width - new_w) / 2 - 0.1)
        top = round((self.height - new_h) / 2 - 0.1)
        canvas = Image.new("RGB", (self.width, self.height), (114, 114, 114))
        canvas.paste(image.resize((new_w, new_h), Image.BILINEAR), (left, top))
        tensor = np.asarray(canvas, dtype=np.float32).transpose(2, 0, 1)[None] / 255.0
        return tensor, gain, left, top

    def predict(self, image: Image.Image, conf: float) -> list[tuple[str, float, list[float]]]:
        """Returns (class name, confidence, [x1, y1, x2, y2] in original pixels), best first."""
        tensor, gain, left, top = self._letterbox(image)
        output = self.session.run(None, {self.input_name: tensor})[0][0].T  # (anchors, 4 + classes)
        scores = output[:, 4:]
        class_ids = scores.argmax(axis=1)
        confidences = scores[np.arange(len(scores)), class_ids]
        keep = confidences > conf
        boxes, class_ids, confidences = output[keep, :4], class_ids[keep], confidences[keep]

        xyxy = np.empty_like(boxes)
        xyxy[:, :2] = boxes[:, :2] - boxes[:, 2:] / 2
        xyxy[:, 2:] = boxes[:, :2] + boxes[:, 2:] / 2
        kept = _nms(xyxy + class_ids[:, None] * CLASS_OFFSET, confidences)[:MAX_DETECTIONS]

        w, h = image.size
        results = []
        for i in kept:
            x1, y1, x2, y2 = xyxy[i]
            box = [
                float(np.clip((x1 - left) / gain, 0, w)),
                float(np.clip((y1 - top) / gain, 0, h)),
                float(np.clip((x2 - left) / gain, 0, w)),
                float(np.clip((y2 - top) / gain, 0, h)),
            ]
            results.append((self.names[int(class_ids[i])], float(confidences[i]), box))
        return results


def _nms(boxes: np.ndarray, scores: np.ndarray) -> list[int]:
    order = scores.argsort()[::-1]
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    kept = []
    while order.size:
        i = order[0]
        kept.append(int(i))
        rest = order[1:]
        iw = np.clip(np.minimum(boxes[i, 2], boxes[rest, 2]) - np.maximum(boxes[i, 0], boxes[rest, 0]), 0, None)
        ih = np.clip(np.minimum(boxes[i, 3], boxes[rest, 3]) - np.maximum(boxes[i, 1], boxes[rest, 1]), 0, None)
        inter = iw * ih
        iou = inter / (areas[i] + areas[rest] - inter)
        order = rest[iou <= IOU_THRESHOLD]
    return kept
