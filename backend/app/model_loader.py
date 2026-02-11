import os
import torch
import joblib
from sklearn.ensemble import RandomForestClassifier
import networkx as nx
import torch.nn as nn
import torch.nn.functional as F
import logging

logger = logging.getLogger("model_loader")
logging.basicConfig(level=logging.INFO)

MODELS_DIR = os.path.join(os.path.dirname(__file__), '../models')
GNN_MODEL_PATH = os.path.join(MODELS_DIR, 'gnn_model.pt')
BASELINE_MODEL_PATH = os.path.join(MODELS_DIR, 'baseline_rf.joblib')

class GraphSAGE(nn.Module):
    def __init__(self, in_feats=10, hidden_feats=16, out_feats=2):
        super().__init__()
        self.fc1 = nn.Linear(in_feats, hidden_feats)
        self.fc2 = nn.Linear(hidden_feats, out_feats)

    def forward(self, x, adj):
        h = F.relu(self.fc1(x))
        h = torch.matmul(adj, h)
        h = self.fc2(h)
        return h

class ModelLoader:
    def __init__(self):
        self.gnn_model = None
        self.baseline_model = None
        self.models_loaded = False
        logger.info("ModelLoader initialized")
        self._ensure_models()

    def _ensure_models(self):
        os.makedirs(MODELS_DIR, exist_ok=True)
        # GNN Model
        if not os.path.exists(GNN_MODEL_PATH):
            self._save_placeholder_gnn()
        # Baseline Model
        if not os.path.exists(BASELINE_MODEL_PATH):
            self._save_placeholder_baseline()
        self._load_models()

    def _save_placeholder_gnn(self):
        model = GraphSAGE()
        dummy_x = torch.randn(1, 10)
        dummy_adj = torch.eye(1)
        with torch.no_grad():
            model(dummy_x, dummy_adj)
        torch.save(model.state_dict(), GNN_MODEL_PATH)
        logger.warning("Fallback: GraphSAGE placeholder model created")

    def _save_placeholder_baseline(self):
        clf = RandomForestClassifier(n_estimators=1)
        X = [[0.0]*10, [1.0]*10]
        y = [0, 1]
        clf.fit(X, y)
        joblib.dump(clf, BASELINE_MODEL_PATH)
        logger.warning("Fallback: RandomForest placeholder model created")

    def _load_models(self):
        try:
            model = GraphSAGE()
            model.load_state_dict(torch.load(GNN_MODEL_PATH))
            model.eval()
            self.gnn_model = model
            self.baseline_model = joblib.load(BASELINE_MODEL_PATH)
            self.models_loaded = True
            logger.info("Models loaded successfully")
        except Exception:
            self.models_loaded = False
            logger.error("Model loading failed; fallback activated")

    def is_ready(self):
        return self.models_loaded

    async def predict(self, flows, use_gnn=True, use_baseline=True, use_cache=True):
        """
        Dummy predict method for placeholder models.
        Returns a fixed benign/malware prediction with confidence.
        """
        logger.info("Inference request received")
        # For demonstration, always return benign with 0.5 confidence
        return {
            'gnn_prediction': {
                'model_name': 'GraphSAGE',
                'predicted_label': 'benign',
                'confidence': 0.5,
                'probabilities': {'benign': 0.5, 'malware': 0.5}
            },
            'baseline_predictions': {
                'RandomForest': {
                    'model_name': 'RandomForest',
                    'predicted_label': 'benign',
                    'confidence': 0.5,
                    'probabilities': {'benign': 0.5, 'malware': 0.5}
                }
            },
            'graph_features': {
                'num_nodes': 1,
                'num_edges': 0,
                'avg_degree': 0.0,
                'density': 0.0,
                'graph_diameter': 0.0,
                'average_clustering': 0.0
            }
        }


