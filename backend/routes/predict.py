
from fastapi import APIRouter, HTTPException, Request
from backend.schemas.request import PredictRequest
from backend.schemas.response import PredictResponse
from backend.services.model_loader import ModelLoader
from backend.services.inference_service import InferenceService
import logging
import traceback
import os

router = APIRouter()
logger = logging.getLogger("PredictRoute")
DEBUG = os.environ.get("NODE_ENV", "production") == "development"

# Load model once and cache
model_loader = ModelLoader("models/gnn_model.pt")
model_loader.load()
inference_service = InferenceService(model_loader)

@router.post("/predict", tags=["Malware Analysis"])
async def predict(request: PredictRequest):
    try:
        logger.info(f"Received request: features={len(request.features)}, edges={len(request.edges)}, node_count={request.node_count}")
        # Input validation
        if not request.features or not request.edges or request.node_count <= 0:
            logger.error("Invalid input: features, edges, or node_count missing/invalid")
            return {"success": False, "error": "Invalid input format: features, edges, and node_count are required"}
        if len(request.features) != request.node_count:
            logger.error("features length does not match node_count")
            return {"success": False, "error": "features length does not match node_count"}
        for edge in request.edges:
            if any(idx >= request.node_count or idx < 0 for idx in edge):
                logger.error("Edge index out of bounds")
                return {"success": False, "error": "Edge index out of bounds"}
        # Model loaded check
        if not model_loader.model:
            logger.error("Model file missing or failed to load")
            return {"success": False, "error": "Model file missing or failed to load"}
        # Prediction
        pred_idx, confidence = inference_service.predict(
            request.features, request.edges, request.node_count
        )
        logger.info(f"Prediction: class={pred_idx}, confidence={confidence}")
        return {
            "success": True,
            "prediction": str(pred_idx),
            "confidence": confidence
        }
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Prediction error: {e}\n{tb}")
        return {
            "success": False,
            "error": f"Prediction error: {e}",
            "trace": tb
        }

@router.get("/predict")
def predict_get():
    return {"error": "Use POST method with JSON body to get predictions."}
