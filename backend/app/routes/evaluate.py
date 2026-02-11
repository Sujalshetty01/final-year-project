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
    """Return confusion matrix and ROC curve data for last predictions (demo).

    This endpoint is defensive: cached results may be Pydantic models or plain dicts.
    """
    results = getattr(request.app.state, 'results_cache', {}) or {}

    def _get(obj, attr, default=None):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(attr, default)
        return getattr(obj, attr, default)

    ys = []
    preds = []
    probs = []

    for res in results.values():
        gnn = _get(res, 'gnn_prediction')
        if not gnn:
            continue

        # Primary label and confidence may live on the response or inside gnn_prediction
        binary_label = _get(res, 'binary_classification') or _get(gnn, 'predicted_label')
        binary_conf = _get(res, 'binary_confidence') or _get(gnn, 'confidence')

        if binary_label is None:
            continue

        y = 1 if str(binary_label).lower() == 'malware' else 0
        p = 1 if str(binary_label).lower() == 'malware' else 0
        prob = None

        # Try to extract malware probability from different shapes
        probs_obj = None
        if isinstance(gnn, dict):
            probs_obj = gnn.get('probabilities')
        else:
            probs_obj = getattr(gnn, 'probabilities', None)

        if isinstance(probs_obj, dict):
            prob = probs_obj.get('malware') or probs_obj.get('1') or binary_conf
        elif isinstance(probs_obj, (list, tuple)) and len(probs_obj) >= 2:
            # assume [benign, malware]
            try:
                prob = float(probs_obj[1])
            except Exception:
                prob = binary_conf
        else:
            try:
                prob = float(binary_conf) if binary_conf is not None else None
            except Exception:
                prob = None

        ys.append(y)
        preds.append(p)
        if prob is not None:
            probs.append(float(prob))

    if not ys:
        raise HTTPException(status_code=404, detail='No cached results to evaluate')

    # Confusion matrix
    try:
        cm = confusion_matrix(ys, preds).tolist()
    except Exception:
        cm = []

    # ROC: require at least one positive and one negative sample and probabilities
    roc_data = {'fpr': [], 'tpr': [], 'thresholds': []}
    try:
        if len(set(ys)) > 1 and len(probs) == len(ys):
            fpr, tpr, thresholds = roc_curve(ys, probs)
            roc_data = {'fpr': fpr.tolist(), 'tpr': tpr.tolist(), 'thresholds': thresholds.tolist()}
    except Exception:
        roc_data = {'fpr': [], 'tpr': [], 'thresholds': []}

    return {
        'confusion_matrix': cm,
        'roc_curve': roc_data
    }
