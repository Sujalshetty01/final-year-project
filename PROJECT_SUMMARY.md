# Project Summary — IEEE-style Report

## Abstract
This project develops a graph-based machine learning pipeline for network-flow classification. We propose a Graph Neural Network (GNN) approach combined with lightweight preprocessing and an evaluation suite for reproducible training, model export (ONNX), and backend inference via FastAPI. Experiments on synthetic flow-derived data demonstrate accurate classification with efficient inference and practical deployment considerations.

## Introduction
Network flow analysis is central to modern traffic classification and threat detection. Traditional feature-based models often miss structural relationships between flows and hosts. We apply GNN architectures to capture relational patterns in flow graphs, improving detection of complex, multi-hop behaviors.

## Methods
- Data: Synthetic network-flow dataset generated to mimic flow records; samples converted into small graphs where nodes represent endpoints/ports and edges represent flows.
- Models: GraphSAGE/GCN-style encoders trained with cross-entropy loss for binary classification. A RandomForest baseline is included for comparison.
- Training: PyTorch-based training pipeline with on-disk dataset support and padding to fixed node counts for batching. Models are exported to ONNX for client-side inference.
- Backend: FastAPI server for model serving, health and analysis endpoints, with Prometheus metrics and JWT-based auth design for future extensions.

## Experiments and Results
Training runs on the synthetic dataset produce stable convergence within 30 epochs on standard workstation hardware. Representative metrics from a recent run:
- Test accuracy: ~0.87
- AUC: >0.90 (baseline-dependent)

Evaluation artifacts (confusion matrices, ROC plots, and detailed per-class reports) are written to `out/eval/` for each run, enabling audit and reproducibility.

## Deployment
Models are exported to ONNX to support lightweight client inference (WebAssembly/ONNX Runtime) and server-side inference (PyTorch/ONNX Runtime). The FastAPI backend exposes `/api/v1/analyze` and `/api/v1/health` endpoints and includes example integration tests.

## Reproducibility & CI
Repository includes scripts to: generate synthetic data, train/evaluate models, sanitize JSON artifacts, and run smoke tests against the backend. CI workflows attempt conservative automated fixes for common issues and upload failure artifacts for inspection.

## Discussion
GNNs effectively leverage relational structure in flow data, improving detection of complex patterns compared to flat feature baselines. Future work includes expanding to real-world flow captures, semi-supervised pretraining on large unlabeled graphs, and robust model explainability for security analysts.

## Conclusion
This project demonstrates an end-to-end GNN pipeline for flow classification, from synthetic data generation through training, evaluation, ONNX export, and serving. The codebase emphasizes reproducibility, modularity, and practical deployment.

## References
1. Hamilton, W., Ying, Z., & Leskovec, J. (2017). Inductive Representation Learning on Large Graphs. arXiv preprint arXiv:1706.02216.
2. Kipf, T. N., & Welling, M. (2017). Semi-Supervised Classification with Graph Convolutional Networks. ICLR.
