import torch
from torch_geometric.data import Data

def preprocess_graph(features, edges, node_count):
    """
    Preprocess graph input for GNN model.
    Args:
        features: List[List[float]] - node features
        edges: List[List[int]] - edge list [[src, dst], ...]
        node_count: int - number of nodes
    Returns:
        torch_geometric.data.Data object
    """
    import numpy as np
    # Validate input shapes
    if len(features) != node_count:
        raise ValueError("features length does not match node_count")
    for edge in edges:
        if any(idx >= node_count or idx < 0 for idx in edge):
            raise ValueError("Edge index out of bounds")
    x = torch.tensor(np.array(features, dtype=float), dtype=torch.float)
    edge_index = torch.tensor(np.array(edges, dtype=int), dtype=torch.long).t().contiguous()
    data = Data(x=x, edge_index=edge_index)
    return data
