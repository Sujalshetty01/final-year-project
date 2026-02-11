import os
import torch
import joblib
from sklearn.ensemble import RandomForestClassifier
import networkx as nx
import torch.nn as nn
import torch.nn.functional as F
import logging
from prometheus_client import Counter

logger = logging.getLogger("model_loader")
logging.basicConfig(level=logging.INFO)

# Prometheus metrics
INFERENCE_COUNTER = Counter('malware_inference_requests_total', 'Total inference requests')

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

    def get_status(self) -> dict:
        return {
            'models_loaded': self.models_loaded,
            'gnn': self.gnn_model is not None,
            'baseline': self.baseline_model is not None
        }

    def is_ready(self):
        return self.models_loaded

    async def predict(self, flows, use_gnn=True, use_baseline=True, use_cache=True):
        """
        Dummy predict method for placeholder models.
        Returns a fixed benign/malware prediction with confidence.
        """
        logger.info("Inference request received")
        try:
            INFERENCE_COUNTER.inc()
        except Exception:
            pass
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

    def explain(self, node_idx: int = 0, **kwargs) -> dict:
        """Return explanation for a node using GNNExplainer when available."""
        try:
            from torch_geometric.explain import GNNExplainer
            if self.gnn_model is None:
                return {'error': 'GNN model not loaded'}
            self.gnn_model.eval()
            explainer = GNNExplainer(self.gnn_model, epochs=20)
            # For placeholder, create small graph tensors
            x = torch.randn(5, 10)
            edge_index = torch.tensor([[0,1,2,3],[1,2,3,4]], dtype=torch.long)
            node_feat_mask, edge_mask = explainer.explain_node(node_idx, x, edge_index)
            return {
                'node_feat_mask': node_feat_mask.tolist() if hasattr(node_feat_mask, 'tolist') else [],
                'edge_mask': edge_mask.tolist() if hasattr(edge_mask, 'tolist') else []
            }
        except Exception as e:
            logger.warning(f'Explainability not available: {e}')
            return {'error': 'explainability not available', 'detail': str(e)}


