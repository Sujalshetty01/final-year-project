from pydantic import BaseModel
from typing import Any, List

class PredictRequest(BaseModel):
    # Example: features, edges, node count, etc.
    features: List[Any]
    edges: List[List[int]]
    node_count: int
    # Add more fields as needed for your GNN
