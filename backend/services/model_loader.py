import torch
import logging

class ModelLoader:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger = logging.getLogger("ModelLoader")

    def load(self):
        try:
            from model.gnn_model import GCN
            # Hardcoded for Cora dataset, adjust as needed
            num_node_features = 1433
            num_classes = 7
            model = GCN(num_node_features, num_classes)
            state_dict = torch.load(self.model_path, map_location=self.device)
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()
            self.model = model
            self.logger.info(f"Model loaded from {self.model_path} on {self.device}")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            self.model = None

    def predict(self, graph_data):
        if self.model is None:
            raise RuntimeError("Model not loaded")
        with torch.no_grad():
            output = self.model(graph_data)
            return output

    def get_info(self):
        return {
            "name": getattr(self.model, "__class__", type(self.model)).__name__,
            "device": str(self.device),
            "loaded": self.model is not None
        }
