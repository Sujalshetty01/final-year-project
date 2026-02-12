"""Generate a small synthetic dataset for GNN demo and evaluation.

Creates a torch-saved dict with keys 'X' and 'y'. Each X[i] is a node-feature
matrix shaped (nodes, feats). The labels are assigned by a simple rule so
that models can learn structural patterns.
"""
import argparse
import os
import random
from datetime import datetime
import numpy as np
import torch
import networkx as nx

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


def make_graph_features(n_nodes, feat_dim=10):
    # generate a random graph with some structural signal
    p = min(0.1 + n_nodes * 0.01, 0.6)
    G = nx.erdos_renyi_graph(n_nodes, p, seed=random.randint(0, 1<<30))
    # node features: degree + random noise
    feats = np.zeros((n_nodes, feat_dim), dtype=float)
    degrees = np.array([d for _, d in G.degree()])
    for i in range(feat_dim):
        feats[:, i] = degrees + np.random.normal(scale=0.1, size=n_nodes)
    # normalize
    feats = (feats - feats.mean()) / (feats.std() + 1e-6)
    metrics = {
        'num_nodes': n_nodes,
        'num_edges': G.number_of_edges(),
        'density': nx.density(G),
        'avg_degree': float(degrees.mean()) if len(degrees)>0 else 0.0
    }
    return feats.astype(np.float32), metrics


def generate(n=200, max_nodes=20, feat_dim=10):
    X = []
    y = []
    metas = []
    for i in range(n):
        nodes = random.randint(4, max_nodes)
        feats, metrics = make_graph_features(nodes, feat_dim=feat_dim)
        # labeling rule: graphs with higher avg_degree and density are more likely malware
        score = metrics['avg_degree'] * 0.6 + metrics['density'] * 0.4 + np.random.normal(scale=0.5)
        label = 1 if score > (max_nodes * 0.15) else 0
        X.append(feats)
        y.append(label)
        metas.append(metrics)
    return X, y, metas


def save(path, X, y, metas=None):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    data = {'X': X, 'y': y}
    if metas is not None:
        data['graph_metrics'] = metas
    torch.save(data, path)


def cli():
    p = argparse.ArgumentParser()
    p.add_argument('--out', default='data/dataset.pth')
    p.add_argument('--n', type=int, default=200)
    p.add_argument('--max-nodes', type=int, default=20)
    p.add_argument('--feat-dim', type=int, default=10)
    args = p.parse_args()
    X, y, metas = generate(n=args.n, max_nodes=args.max_nodes, feat_dim=args.feat_dim)
    save(args.out, X, y, metas)
    print(f'Wrote synthetic dataset to {args.out} (n={args.n})')


if __name__ == '__main__':
    cli()
