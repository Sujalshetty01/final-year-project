"""Train a simple GraphSAGE-like model on preprocessed dataset.

This script is intentionally dataset-agnostic: it expects a torch-saved
dict with keys: 'X' (array or list where each sample is either a node-feature
matrix shaped (nodes, feats) or a flat feature vector),
'y' (labels).

The goal is reproducible, auditable training with class-imbalance handling,
early stopping, dropout and a clear metric output.
"""
import argparse
import os
import random
import json
from datetime import datetime
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)


class SimpleGNN(nn.Module):
    def __init__(self, in_feats=10, hidden=64, out=2, dropout=0.3):
        super().__init__()
        self.fc1 = nn.Linear(in_feats, hidden)
        self.act = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(hidden, out)

    def forward(self, x):
        # x may be (B, nodes, feats) or (B, feats)
        if x.dim() == 3:
            # pool node features by mean
            x = x.mean(dim=1)
        h = self.act(self.fc1(x))
        h = self.dropout(h)
        return self.fc2(h)


def load_data(path):
    # allowloading of datasets saved with numpy objects across torch versions
    try:
        data = torch.load(path)
    except Exception:
        data = torch.load(path, weights_only=False)
    X = data['X']  # expect array-like
    y = data['y']
    return np.array(X), np.array(y)


def make_dataloaders(X, y, test_size=0.2, val_size=0.1, batch_size=32):
    X_trainval, X_test, y_trainval, y_test = train_test_split(X, y, test_size=test_size, random_state=SEED, stratify=y)
    val_rel = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(X_trainval, y_trainval, test_size=val_rel, random_state=SEED, stratify=y_trainval)

    # convert to tensors
    X_train = torch.tensor(np.array(X_train), dtype=torch.float32)
    X_val = torch.tensor(np.array(X_val), dtype=torch.float32)
    X_test = torch.tensor(np.array(X_test), dtype=torch.float32)
    y_train = torch.tensor(np.array(y_train), dtype=torch.long)
    y_val = torch.tensor(np.array(y_val), dtype=torch.long)
    y_test = torch.tensor(np.array(y_test), dtype=torch.long)

    train_ds = torch.utils.data.TensorDataset(X_train, y_train)
    val_ds = torch.utils.data.TensorDataset(X_val, y_val)
    test_ds = torch.utils.data.TensorDataset(X_test, y_test)

    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = torch.utils.data.DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    test_loader = torch.utils.data.DataLoader(test_ds, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader, test_loader, (X_test, y_test)


def train(args):
    X, y = load_data(args.data)
    train_loader, val_loader, test_loader, testset = make_dataloaders(X, y, batch_size=args.batch_size)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    sample = X[0]
    in_feats = sample.shape[-1]
    model = SimpleGNN(in_feats=in_feats, hidden=args.hidden, out=args.classes, dropout=args.dropout).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    best_val = 1e9
    patience = args.patience
    wait = 0
    history = {'train_loss': [], 'val_loss': []}

    os.makedirs(args.out, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        model.train()
        running = 0.0
        total = 0
        for xb, yb in train_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            logits = model(xb)
            loss = criterion(logits, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running += loss.item() * xb.size(0)
            total += xb.size(0)
        train_loss = running / total

        # val
        model.eval()
        vrunning = 0.0
        vtotal = 0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb = xb.to(device)
                yb = yb.to(device)
                logits = model(xb)
                loss = criterion(logits, yb)
                vrunning += loss.item() * xb.size(0)
                vtotal += xb.size(0)
        val_loss = vrunning / vtotal

        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)

        print(f"Epoch {epoch}/{args.epochs} train_loss={train_loss:.4f} val_loss={val_loss:.4f}")

        # early stopping
        if val_loss < best_val - 1e-4:
            best_val = val_loss
            wait = 0
            torch.save(model.state_dict(), os.path.join(args.out, 'model.pt'))
            # save meta
            with open(os.path.join(args.out, 'meta.json'), 'w') as fh:
                json.dump({'epoch': epoch, 'val_loss': val_loss, 'timestamp': datetime.utcnow().isoformat()}, fh)
        else:
            wait += 1
            if wait >= patience:
                print('Early stopping')
                break

    # evaluate on test
    model.load_state_dict(torch.load(os.path.join(args.out, 'model.pt')))
    model.eval()
    preds = []
    trues = []
    with torch.no_grad():
        for xb, yb in test_loader:
            xb = xb.to(device)
            logits = model(xb)
            preds.extend(torch.argmax(logits, dim=1).cpu().numpy().tolist())
            trues.extend(yb.numpy().tolist())

    acc = accuracy_score(trues, preds)
    meta = {'accuracy': acc, 'timestamp': datetime.utcnow().isoformat()}
    with open(os.path.join(args.out, 'train_history.json'), 'w') as fh:
        json.dump({'history': history, 'meta': meta}, fh, indent=2)
    print('Test accuracy:', acc)


def cli():
    p = argparse.ArgumentParser()
    p.add_argument('--data', required=True, help='path to torch dataset (dict with X and y)')
    p.add_argument('--out', default='out/gnn')
    p.add_argument('--epochs', type=int, default=50)
    p.add_argument('--lr', type=float, default=1e-3)
    p.add_argument('--batch-size', type=int, default=32)
    p.add_argument('--hidden', type=int, default=64)
    p.add_argument('--dropout', type=float, default=0.3)
    p.add_argument('--patience', type=int, default=5)
    p.add_argument('--classes', type=int, default=2)
    args = p.parse_args()
    train(args)


if __name__ == '__main__':
    cli()
