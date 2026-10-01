from pydantic import BaseModel, Field

class Detection(BaseModel):
    label: str
    confidence: float
    bbox: list[float]

class DetectionResponse(BaseModel):
    objects: list[Detection]
    
class NormalizedBBox(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    w: float = Field(ge=0, le=1)
    h: float = Field(ge=0, le=1)

class AnalyzeObject(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)
    bbox: NormalizedBBox
    
class AnalyzeResponse(BaseModel):
    modelVersion: str
    processingTimeMs: float = Field(ge=0)
    objects: list[AnalyzeObject] = Field(default_factory=list)