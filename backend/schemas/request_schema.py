from pydantic import BaseModel
from typing import List

class PredictRequest(BaseModel):
    features: List[List[float]]
    edges: List[List[int]]
    node_count: int
