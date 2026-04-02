import torch
from backend.utils.logger import setup_logger

class InferenceService:
    def __init__(self, model_loader):
        self.logger = setup_logger("InferenceService")
        self.model_loader = model_loader

    def predict(self, features, edges, node_count):
        if not self.model_loader.model:
            self.logger.error("Model not loaded.")
            raise RuntimeError("Model not loaded.")
        try:
            from backend.utils.preprocessing import preprocess_graph
            graph_data = preprocess_graph(features, edges, node_count)
            graph_data = graph_data.to(self.model_loader.device)
            with torch.no_grad():
                output = self.model_loader.model(graph_data)
                prob = torch.exp(output)  # log_softmax -> exp for probabilities
                pred_idx = torch.argmax(prob, dim=1).item()
                confidence = prob[0, pred_idx].item() if prob.ndim == 2 else prob[pred_idx].item()
                return pred_idx, confidence
        except Exception as e:
            self.logger.error(f"Inference error: {e}")
            raise
