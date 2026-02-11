from __future__ import annotations

from typing import Tuple
import torch
from torch_geometric.data import Data


def synthetic_graph() -> Data:
    # small synthetic graph for reproducible runs
    x = torch.randn((5, 10))
    edge_index = torch.tensor([[0,1,2,3],[1,2,3,4]], dtype=torch.long)
    y = torch.tensor([0,1,0,1,0], dtype=torch.long)
    return Data(x=x, edge_index=edge_index, y=y)


def load_dataset() -> Tuple[list[Data], list[Data], list[Data]]:
    # For review/demo: split synthetic dataset into train/val/test
    graphs = [synthetic_graph() for _ in range(50)]
    train = graphs[:35]
    val = graphs[35:42]
    test = graphs[42:]
    return train, val, test
