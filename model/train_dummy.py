# train_dummy.py
"""
Train a GCN model matching the dummy graph dimensions (2 node features, 2 classes).
"""

import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from gnn_model import GCN, train, test

# Dummy graph data
x = torch.tensor([[1.0, 0.5], [0.2, 0.8], [0.9, 0.1]], dtype=torch.float)
edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.long)
y = torch.tensor([0, 1, 0], dtype=torch.long)  # Example labels

# Masks for training/testing
train_mask = torch.tensor([True, True, False])
test_mask = torch.tensor([False, False, True])

data = Data(x=x, edge_index=edge_index, y=y, train_mask=train_mask, test_mask=test_mask)

model = GCN(num_node_features=2, num_classes=2)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
criterion = torch.nn.CrossEntropyLoss()

for epoch in range(1, 101):
    loss = train(model, data, optimizer, criterion)
    if epoch % 10 == 0:
        acc = test(model, data)
        print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}, Test Acc: {acc:.4f}')

# Save model weights
model_path = 'model/gnn_model.pt'
torch.save(model.state_dict(), model_path)
print(f'Model saved as {model_path}')
