"""Helper to validate environment and files before running evaluate_models.py

Usage:
  python run_evaluation_check.py --gnn model.pt --data data.pt --out out/eval

What it does:
- Checks required Python packages (torch, sklearn, numpy, matplotlib, reportlab)
- Checks that the model and data files exist
- If missing packages, prints a pip install command
- If files missing, prints how to generate synthetic data with generate_synthetic.py
- If all good, prints the exact command to run `evaluate_models.py`
"""
import argparse
import os
import importlib

REQS = [
    ('torch', 'torch'),
    ('numpy', 'numpy'),
    ('sklearn', 'scikit-learn'),
    ('matplotlib', 'matplotlib'),
    ('reportlab', 'reportlab'),
]

INSTALL_CMDS = []


def check_packages():
    missing = []
    for mod, pkg in REQS:
        try:
            importlib.import_module(mod)
        except Exception:
            missing.append(pkg)
    return missing


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--gnn', required=True, help='Path to trained GNN model (pth/pt)')
    p.add_argument('--data', required=True, help='Path to dataset torch file (created by generate_synthetic.py)')
    p.add_argument('--out', default='out/eval', help='Output directory for evaluation artifacts')
    args = p.parse_args()

    missing_pkgs = check_packages()
    if missing_pkgs:
        print('Missing Python packages:')
        for pkg in missing_pkgs:
            print(' -', pkg)
        print('\nInstall with:')
        print('  pip install ' + ' '.join(missing_pkgs))
    else:
        print('All required Python packages appear installed.')

    gnn_exists = os.path.exists(args.gnn)
    data_exists = os.path.exists(args.data)

    if not gnn_exists:
        print(f"\nModel file not found: {args.gnn}")
        print("If you don't have a trained model yet, run training/train_gnn.py to create one (see training/README.md).")
    else:
        print(f"Model file found: {args.gnn}")

    if not data_exists:
        print(f"\nData file not found: {args.data}")
        print("You can generate a deterministic synthetic dataset with:")
        print("  python training/generate_synthetic.py --out synthetic_data.pt --n 200 --seed 42")
    else:
        print(f"Data file found: {args.data}")

    if (not missing_pkgs) and gnn_exists and data_exists:
        print('\nReady to run evaluation. Run:')
        print(f'  python training/evaluate_models.py --gnn {args.gnn} --data {args.data} --out {args.out}')
    else:
        print('\nOnce dependencies and files are present, run the evaluation command above.')


if __name__ == '__main__':
    main()
