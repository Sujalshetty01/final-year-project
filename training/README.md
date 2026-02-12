Phase 2: Offline training and evaluation

This folder contains safe, offline-only scripts to train, evaluate and
generate reproducible reports for the GNN and baseline models. These
do not modify the deployed API and are intended for local experiments
and academic evaluation.

Quick start (assumes Python 3.11 venv):

1. Create venv and install deps:

   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt

2. Prepare dataset: see `DATA_FORMAT.md` (expects a pickled dataset or CSVs).

3. Train and evaluate:

   python train_gnn.py --data data/dataset.pth --out out/gnn
   python evaluate_models.py --data data/dataset.pth --gnn out/gnn/model.pt --out out/eval

If you don't have a dataset ready, generate a small synthetic dataset for demo and validation:

```bash
python generate_synthetic.py --out data/dataset.pth --n 200 --max-nodes 16
```

Outputs:
- trained model checkpoints in `out/`.
- evaluation JSON and plots in `out/eval/` including ROC, confusion matrix, and training curves.
- PDF report generator (via `evaluate_models.py`) creates `evaluation_report.pdf`.

Design notes:
- Uses deterministic seeding for reproducibility.
- Handles class imbalance with weighted sampler and class weights.
- Includes early stopping and dropout.
- Produces metrics: accuracy, precision, recall, F1, ROC-AUC, confusion matrix.
