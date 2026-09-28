from pydantic import BaseModel

class Detection(BaseModel):
    label: str
    confidence: float
    bbox: list[float]

class DetectionResponse(BaseModel):
    objects: list[Detection]