"""
Health check endpoints
Includes /health and /ready endpoints for monitoring
"""

from fastapi import APIRouter, Request
from datetime import datetime
from app.models.schemas import HealthResponse, ReadyResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """
    Health check endpoint
    Returns status of API and models
    """
    model_loader = request.app.state.model_loader
    
    status_data = {
        'status': 'healthy',
        'timestamp': datetime.now(),
        'version': '1.0.0',
        'models_loaded': model_loader.is_ready() if model_loader else False,
        'models_status': {
            'gnn': model_loader.gnn_model is not None if model_loader else False,
            'baseline': model_loader.baseline_model is not None if model_loader and hasattr(model_loader, 'baseline_model') else False
        },
        'cache_stats': model_loader.cache.stats() if model_loader and hasattr(model_loader, 'cache') else None
    }
    if not status_data['models_loaded']:
        status_data['status'] = 'degraded'
    return HealthResponse(**status_data)


@router.get("/ready", response_model=ReadyResponse)
async def readiness_check(request: Request) -> ReadyResponse:
    """
    Readiness check endpoint
    Returns true only if service is ready to accept inference requests
    """
    model_loader = request.app.state.model_loader
    
    ready = False
    reason = None
    
    if model_loader is None:
        reason = "Model loader not initialized"
    elif not model_loader.is_ready():
        reason = "Models not loaded"
    elif model_loader.gnn_model is None:
        reason = "GNN model not available"
    else:
        ready = True
    return ReadyResponse(
        ready=ready,
        reason=reason,
        timestamp=datetime.now()
    )
