"""Export trained PyTorch GNN checkpoint to ONNX at out/models/model.onnx

Usage:
  python scripts/export_onnx.py --checkpoint training/model.pt --out out/models/model.onnx
"""
import os
import argparse
import torch

from training.train_gnn import SimpleGNN


def export(checkpoint, out_path):
    if not os.path.exists(checkpoint):
        raise FileNotFoundError(checkpoint)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    state = torch.load(checkpoint, map_location='cpu')
    # state may be a state_dict or full model depending on save
    if isinstance(state, dict) and any(k.startswith('fc1') for k in state.keys()):
        # it's a state_dict
        # infer in_feats from fc1.weight shape
        w = state['fc1.weight']
        in_feats = w.shape[1]
    else:
        # try loading sample via training dataset shape fallback
        # default to 10
        in_feats = 10

    model = SimpleGNN(in_feats=in_feats)
    try:
        model.load_state_dict(state)
    except Exception:
        # maybe checkpoint wraps state
        if isinstance(state, dict) and 'model_state' in state:
            model.load_state_dict(state['model_state'])
        else:
            # best-effort: attempt torch.load of model.pt as state_dict
            model.load_state_dict(state)

    model.eval()

    # create a dummy input: (1, nodes, feats) or (1, feats)
    # use (1, in_feats) to match SimpleGNN handling
    dummy = torch.zeros((1, in_feats), dtype=torch.float32)

    torch.onnx.export(
        model,
        dummy,
        out_path,
        input_names=['input'],
        output_names=['output'],
        opset_version=13,
    )


def cli():
    p = argparse.ArgumentParser()
    p.add_argument('--checkpoint', default='training/model.pt')
    p.add_argument('--out', default='out/models/model.onnx')
    args = p.parse_args()
    export(args.checkpoint, args.out)
    print(f'Exported ONNX model to {args.out}')


if __name__ == '__main__':
    cli()
