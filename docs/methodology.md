# Methodology (Summary)

- **Data Representation:** Network traffic is modeled as graphs, with nodes as hosts and edges as flows.
- **Feature Extraction:** Graph features and flow statistics are extracted for each sample.
- **Modeling:**
  - Graph Neural Network (GNN, e.g., GraphSAGE) for structural learning.
  - Baseline classifier (RandomForest) for tabular features.
- **Pipeline:**
  - Unified ModelLoader loads both models, with fallback to lightweight stubs if missing.
  - API exposes /analyze endpoint for inference.
- **Deployment:**
  - Fully containerized with Docker Compose.
  - Health/readiness endpoints for monitoring.

*This document is for academic review and future extension. See code for details.*
