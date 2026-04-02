from pydantic import BaseModel

class PredictResponse(BaseModel):
    prediction: int
    confidence: float
    message: str = "Prediction successful"
