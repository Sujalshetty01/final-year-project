from __future__ import annotations

from fastapi import APIRouter, Request, Depends, HTTPException
from typing import Any
from sklearn.metrics import confusion_matrix, roc_curve
import numpy as np

router = APIRouter()


def require_auth(request: Request, token=Depends(lambda: None)):
    # token is provided by JWTAuth dependency attached in main via DI
    if token is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    return True


@router.get('/evaluate/summary')
async def evaluation_summary(request: Request, auth=Depends(require_auth)) -> Any:
    """Return confusion matrix and ROC curve data for last predictions (demo)."""
    # For demo, use cached results if available
    # Build confusion matrix from cached results
    results = getattr(request.app.state, 'results_cache', {})
    ys = []
    preds = []
    probs = []
    for res in results.values():
        if res.gnn_prediction:
            ys.append(1 if res.binary_classification == 'malware' else 0)
            preds.append(1 if res.binary_classification == 'malware' else 0)
            probs.append(res.binary_confidence)

    if not ys:
        raise HTTPException(status_code=404, detail='No cached results to evaluate')

    cm = confusion_matrix(ys, preds).tolist()
    fpr, tpr, thresholds = roc_curve(ys, probs)
    return {
        'confusion_matrix': cm,
        'roc_curve': {
            'fpr': fpr.tolist(),
            'tpr': tpr.tolist(),
            'thresholds': thresholds.tolist()
        }
    }
