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
    x = torch.tensor(features, dtype=torch.float)
    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
    data = Data(x=x, edge_index=edge_index)
    return data
