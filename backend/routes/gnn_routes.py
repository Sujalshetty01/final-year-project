from fastapi import APIRouter, HTTPException
from backend.services.model_loader import ModelLoader
from backend.services.inference_service import InferenceService
from backend.schemas.request import PredictRequest
from backend.schemas.response import PredictResponse
import logging


router = APIRouter()
logger = logging.getLogger("GNNRoute")
model_loader = ModelLoader("models/gnn_model.pt")
model_loader.load()
inference_service = InferenceService(model_loader)

@router.get("/health")
def health():
	status = "loaded" if model_loader.model else "not_loaded"
	return {"status": status}

@router.post("/predict", response_model=PredictResponse)
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
# Create modular GNN API endpoints for health and prediction.