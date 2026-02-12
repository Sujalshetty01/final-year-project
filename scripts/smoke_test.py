#!/usr/bin/env python3
"""Smoke test for ONNX model: loads model, runs a tiny inference, exits 0 on success.

Usage:
  python scripts/smoke_test.py --model out/models/model.onnx
"""
import argparse
import json
import sys
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.environ.get("MODEL_PATH", "out/models/model.onnx"))
    args = parser.parse_args()

    try:
        import onnxruntime as ort
        import numpy as np
    except Exception as e:
        print(json.dumps({"ok": False, "error": "onnxruntime or numpy not installed", "detail": str(e)}))
        return 2

    if not os.path.exists(args.model):
        print(json.dumps({"ok": False, "error": "model not found", "path": args.model}))
        return 3

    try:
        sess = ort.InferenceSession(args.model, providers=["CPUExecutionProvider"])
        inp = sess.get_inputs()[0]
        # Build a minimal input using dimensions from the model (replace dynamic dims with 1)
        shape = [1 if (d is None or isinstance(d, str)) else max(1, int(d)) for d in inp.shape]
        x = np.zeros(tuple(shape), dtype=np.float32)
        # seed with small non-zero values to exercise ops
        flat = x.ravel()
        flat[:min(4, flat.size)] = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)[:min(4, flat.size)]
        out = sess.run(None, {inp.name: x})
        # summarize output
        out0 = out[0]
        scalar = float(np.asarray(out0).ravel()[0]) if hasattr(out0, 'tolist') else float(out0)
        print(json.dumps({"ok": True, "model": args.model, "output_sample": float(scalar)}))
        return 0
    except Exception as e:
        print(json.dumps({"ok": False, "error": "inference_failed", "detail": str(e)}))
        return 4

if __name__ == "__main__":
    sys.exit(main())
