from __future__ import annotations

import os
import time
from typing import List

import torch
import torch.nn.functional as F
from torch_geometric.loader import DataLoader
from torch import nn
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score

from app.training.dataset import load_dataset
from app.model_registry import save_metadata

MODELS_DIR = os.path.join(os.path.dirname(__file__), '../../models')
os.makedirs(MODELS_DIR, exist_ok=True)


class GNN(nn.Module):
    def __init__(self, in_feats=10, hidden=16, out_feats=2):
        super().__init__()
        self.lin1 = nn.Linear(in_feats, hidden)
        self.lin2 = nn.Linear(hidden, out_feats)

    def forward(self, data):
        x = data.x
        h = F.relu(self.lin1(x))
        h = self.lin2(h)
        # global pooling (mean)
        return h.mean(dim=0, keepdim=True)


def evaluate_model(model: nn.Module, loader: DataLoader) -> dict:
    model.eval()
    ys = []
    preds = []
    probs = []
    with torch.no_grad():
        for d in loader:
            out = model(d)
            prob = torch.softmax(out, dim=1).cpu().numpy()
            pred = prob.argmax(axis=1)
            ys.extend(d.y.cpu().numpy().tolist())
            preds.extend(pred.tolist())
            probs.extend(prob[:, 1].tolist())
    metrics = {}
    if ys:
        metrics['accuracy'] = accuracy_score(ys, preds)
        p, r, f1, _ = precision_recall_fscore_support(ys, preds, average='binary', zero_division=0)
        metrics.update({'precision': p, 'recall': r, 'f1': f1})
        try:
            metrics['roc_auc'] = roc_auc_score(ys, probs)
        except Exception:
            metrics['roc_auc'] = None
    return metrics


def train(epochs: int = 10, lr: float = 1e-3):
    train_set, val_set, test_set = load_dataset()
    train_loader = DataLoader(train_set, batch_size=8)
    val_loader = DataLoader(val_set, batch_size=8)
    test_loader = DataLoader(test_set, batch_size=8)

    model = GNN()
    optim = torch.optim.Adam(model.parameters(), lr=lr)

    best_val = -1.0
    best_path = None
    patience = 3
    wait = 0

    for epoch in range(1, epochs+1):
        model.train()
        losses = []
        for batch in train_loader:
            optim.zero_grad()
            out = model(batch)
            # supervise with majority label for demo
            target = batch.y.mean().long().unsqueeze(0)
            loss = F.cross_entropy(out, target)
            loss.backward()
            optim.step()
            losses.append(loss.item())

        val_metrics = evaluate_model(model, val_loader)
        val_score = val_metrics.get('f1', 0.0) or 0.0
        print(f"Epoch {epoch} loss={sum(losses)/len(losses):.4f} val_f1={val_score:.4f}")

        # checkpoint
        version = time.strftime('%Y%m%d%H%M%S')
        path = os.path.join(MODELS_DIR, f'gnn_{version}.pt')
        if val_score > best_val:
            torch.save(model.state_dict(), path)
            save_metadata(version, {'path': path, 'val_metrics': val_metrics})
            best_val = val_score
            best_path = path
            wait = 0
        else:
            wait += 1
            if wait >= patience:
                print('Early stopping')
                break

    # final evaluation
    if best_path:
        model.load_state_dict(torch.load(best_path))
    test_metrics = evaluate_model(model, test_loader)
    print('Test metrics:', test_metrics)
    return test_metrics


if __name__ == '__main__':
    train(epochs=20)
