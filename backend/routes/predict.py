from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.request import PredictRequest
from backend.schemas.response import PredictResponse
from backend.services.model_loader import ModelLoader
from backend.services.inference_service import InferenceService
import logging

router = APIRouter()
logger = logging.getLogger("PredictRoute")
model_loader = ModelLoader("models/gnn_model.pt")
model_loader.load()
inference_service = InferenceService(model_loader)

@router.post("/predict", response_model=PredictResponse, tags=["Malware Analysis"])
def predict(request: PredictRequest):
    try:
        pred_idx, confidence = inference_service.predict(
            request.features, request.edges, request.node_count
        )
        return PredictResponse(
            predicted_class=str(pred_idx),
            confidence=confidence,
            status="success"
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add GET handler for /predict to clarify method usage
@router.get("/predict")
def predict_get():
    return {"error": "Use POST method with JSON body to get predictions."}
