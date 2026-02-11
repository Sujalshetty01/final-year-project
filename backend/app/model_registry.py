from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, Optional

MODELS_DIR = os.path.join(os.path.dirname(__file__), '../models')
os.makedirs(MODELS_DIR, exist_ok=True)


def _meta_path(version: str) -> str:
    return os.path.join(MODELS_DIR, f"model_{version}.json")


def save_metadata(version: str, metadata: Dict) -> None:
    path = _meta_path(version)
    metadata = dict(metadata)
    metadata.setdefault('created_at', datetime.utcnow().isoformat())
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)


def list_models() -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    for fname in os.listdir(MODELS_DIR):
        if fname.endswith('.json') and fname.startswith('model_'):
            version = fname[len('model_'):-len('.json')]
            try:
                with open(os.path.join(MODELS_DIR, fname), 'r', encoding='utf-8') as f:
                    out[version] = json.load(f)
            except Exception:
                out[version] = {}
    return out


def latest_model_version() -> Optional[str]:
    models = list_models()
    if not models:
        return None
    # choose latest by created_at if present
    sorted_versions = sorted(models.items(), key=lambda iv: iv[1].get('created_at', ''), reverse=True)
    return sorted_versions[0][0]
