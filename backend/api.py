# api.py
"""
FastAPI backend API for GNN prediction.
Receives graph data, converts to PyTorch Geometric format, loads GNN model, and returns predictions.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from torch_geometric.data import Data
from model.gnn_model import GCN, predict

app = FastAPI()

class GraphInput(BaseModel):
    x: list  # Node features: [[...], ...]
    edge_index: list  # Edge indices: [[src1, src2, ...], [dst1, dst2, ...]]

@app.post('/predict')
def predict_graph(input: GraphInput):
    try:
        x = torch.tensor(input.x, dtype=torch.float)
        edge_index = torch.tensor(input.edge_index, dtype=torch.long)
        data = Data(x=x, edge_index=edge_index)
        model = GCN(num_node_features=x.shape[1], num_classes=2)  # Adjust num_classes as needed
        model.load_state_dict(torch.load('model/gnn_model.pt', map_location='cpu'))
        pred = predict(model, data)
        return {"prediction": pred.tolist()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
