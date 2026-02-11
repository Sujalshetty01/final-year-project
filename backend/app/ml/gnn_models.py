"""
Graph Neural Network models for malware classification
Includes GCN and GraphSAGE implementations using PyTorch Geometric
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Try to import pytorch_geometric
try:
    from torch_geometric.nn import GCNConv, GraphSAGE, SAGEConv
    from torch_geometric.data import Data
    TORCH_GEOMETRIC_AVAILABLE = True
except ImportError:
    TORCH_GEOMETRIC_AVAILABLE = False
    logger.warning("PyTorch Geometric not available - GNN models will use fallback")


class GNNMalwareClassifier(nn.Module):
    """
    Graph Neural Network for malware classification
    Uses GraphSAGE or GCN architecture
    """
    
    def __init__(
        self,
        in_features: int = 1,
        hidden_dims: list = None,
        num_classes: int = 2,
        dropout: float = 0.5,
        architecture: str = "graphsage"
    ):
        super().__init__()
        
        if hidden_dims is None:
            hidden_dims = [64, 32]
        
        self.architecture = architecture
        self.in_features = in_features
        self.hidden_dims = hidden_dims
        self.num_classes = num_classes
        self.dropout = nn.Dropout(dropout)
        
        if TORCH_GEOMETRIC_AVAILABLE:
            self._build_geometric_model()
        else:
            self._build_fallback_model()
    
    def _build_geometric_model(self):
        """Build model with pytorch_geometric"""
        if self.architecture.lower() == "gcn":
            self.conv1 = GCNConv(self.in_features, self.hidden_dims[0])
            self.conv2 = GCNConv(self.hidden_dims[0], self.hidden_dims[1])
        else:  # graphsage
            self.conv1 = SAGEConv(self.in_features, self.hidden_dims[0])
            self.conv2 = SAGEConv(self.hidden_dims[0], self.hidden_dims[1])
        
        self.classifier = nn.Sequential(
            nn.Linear(self.hidden_dims[1], 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, self.num_classes)
        )
    
    def _build_fallback_model(self):
        """Build fallback model without pytorch_geometric"""
        self.layers = nn.Sequential(
            nn.Linear(self.in_features + 4, 64),  # +4 for aggregated edge features
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.5),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.BatchNorm1d(32),
            nn.Dropout(0.3),
            nn.Linear(32, self.num_classes)
        )
    
    def forward(self, x: torch.Tensor, edge_index: Optional[torch.Tensor] = None,
                edge_attr: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Node feature matrix [num_nodes, in_features]
            edge_index: Edge indices [2, num_edges]
            edge_attr: Edge attributes [num_edges, num_edge_features]
            
        Returns:
            Tuple of (logits, probabilities)
        """
        try:
            if TORCH_GEOMETRIC_AVAILABLE and edge_index is not None:
                # GNN forward pass
                h = self.dropout(x)
                h = self.conv1(h, edge_index)
                h = torch.relu(h)
                h = self.dropout(h)
                h = self.conv2(h, edge_index)
                
                # Global mean pooling
                graph_embedding = h.mean(dim=0, keepdim=True)
                
                logits = self.classifier(graph_embedding)
            else:
                # Fallback: aggregate node features and edge attributes
                if isinstance(x, np.ndarray):
                    x = torch.from_numpy(x).float()
                
                # Simple aggregation
                node_feat = x.mean(dim=0, keepdim=True)  # [1, in_features]
                
                if edge_attr is not None:
                    if isinstance(edge_attr, np.ndarray):
                        edge_attr = torch.from_numpy(edge_attr).float()
                    edge_feat = edge_attr.mean(dim=0, keepdim=True)
                else:
                    edge_feat = torch.zeros(1, 4)
                
                combined = torch.cat([node_feat, edge_feat], dim=1)
                logits = self.layers(combined)
            
            probs = torch.softmax(logits, dim=1)
            return logits, probs
            
        except Exception as e:
            logger.error(f"Error in forward pass: {str(e)}")
            # Return default predictions
            batch_size = 1
            device = x.device if isinstance(x, torch.Tensor) else torch.device('cpu')
            logits = torch.zeros(batch_size, self.num_classes, device=device)
            probs = torch.ones(batch_size, self.num_classes, device=device) / self.num_classes
            return logits, probs


class MLPMalwareClassifier(nn.Module):
    """Simple MLP baseline for comparison"""
    
    def __init__(self, input_dim: int, hidden_dims: list = None, num_classes: int = 2):
        super().__init__()
        
        if hidden_dims is None:
            hidden_dims = [128, 64, 32]
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim),
                nn.Dropout(0.3)
            ])
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, num_classes))
        
        self.model = nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass"""
        if isinstance(x, np.ndarray):
            x = torch.from_numpy(x).float()
        
        logits = self.model(x)
        probs = torch.softmax(logits, dim=-1)
        
        return logits, probs
