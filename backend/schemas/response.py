from pydantic import BaseModel
from typing import Any

class PredictResponse(BaseModel):
    predicted_class: str
    confidence: float
    status: str
    details: Any = None

class ModelInfoResponse(BaseModel):
    name: str
    accuracy: float
    classes: list
    device: str
    loaded: bool
