# train.py
"""
Training script for GCN model using PyTorch Geometric.
Loads graph data, trains the model, evaluates, and saves weights.
"""

import torch
import torch.nn.functional as F
from torch_geometric.datasets import Planetoid
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from gnn_model import GCN, train, test

# Example: Use Cora dataset for demonstration
# Replace with your own graph data as needed
dataset = Planetoid(root='data/Cora', name='Cora')
data = dataset[0]

model = GCN(num_node_features=dataset.num_node_features, num_classes=dataset.num_classes)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
criterion = torch.nn.NLLLoss()

# Training loop
for epoch in range(1, 201):
    loss = train(model, data, optimizer, criterion)
    if epoch % 10 == 0:
        acc = test(model, data)
        print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}, Test Acc: {acc:.4f}')

# Save model weights
import os
os.makedirs('models', exist_ok=True)
torch.save(model.state_dict(), 'models/gnn_model.pt')
print('Model saved as gnn_model.pt')
