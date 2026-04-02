#!/usr/bin/env python3
"""Simple labeled calibration for ONNX model using a few hand-crafted samples.

This script loads out/models/model.onnx, runs the model on each labeled
sample (using the same lightweight feature construction used in the demo),
and performs a grid search over temperature and bias to minimize binary
cross-entropy (NLL). Saves results to out/models/calibration_labeled.json.
"""
import json
import math
import os
from collections import Counter

import numpy as np

try:
    import onnxruntime as ort
except Exception as e:
    raise SystemExit("onnxruntime is required: pip install onnxruntime")


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def build_feature_vector_from_flows(flows):
    # tolerant field extraction
    bytes_list = [
        f.get("bytes")
        or f.get("total_bytes")
        or f.get("size")
        or 0
        for f in flows
    ]
    durations = [f.get("duration") or f.get("dur") or 0 for f in flows]
    ports = [f.get("dst_port") or f.get("dport") or f.get("port") or None for f in flows]

    total_bytes = float(sum(bytes_list))
    total_count = float(len(flows))
    avg_dur = float(np.mean(durations)) if durations else 0.0
    distinct_ports = float(len(set([p for p in ports if p is not None])))
    mean_bytes = float(np.mean(bytes_list)) if bytes_list else 0.0

    max_b = float(np.max(bytes_list)) if bytes_list else 0.0
    min_b = float(np.min(bytes_list)) if bytes_list else 0.0
    std_b = float(np.std(bytes_list)) if bytes_list else 0.0

    counts = Counter([p for p in ports if p is not None])
    if counts:
        probs = np.array(list(counts.values()), dtype=np.float32)
        probs = probs / probs.sum()
        port_entropy = float(-np.sum(probs * np.log2(probs + 1e-12)))
    else:
        port_entropy = 0.0

    # replicate the demo's log1p-based scaling where helpful
    vec = [
        math.log1p(total_bytes),
        math.log1p(total_count),
        math.log1p(avg_dur),
        distinct_ports,
        math.log1p(mean_bytes),
        math.log1p(max_b),
        math.log1p(min_b + 1e-6),
        math.log1p(std_b + 1e-6),
        port_entropy,
    ]

    return np.array(vec, dtype=np.float32)


def load_model(session_path):
    if not os.path.exists(session_path):
        raise FileNotFoundError(session_path)
    sess = ort.InferenceSession(session_path, providers=["CPUExecutionProvider"])
    return sess


def run_on_model(sess, feature_vec):
    inp = sess.get_inputs()[0]
    name = inp.name
    # adapt feature vector length to expected input dim
    shape = inp.shape
    # shape often like ['None', N]
    expected_dim = None
    if isinstance(shape, (list, tuple)) and len(shape) >= 2:
        expected_dim = shape[1]
    arr = feature_vec
    if expected_dim is not None and expected_dim != arr.size:
        if expected_dim > arr.size:
            pad = np.zeros(expected_dim - arr.size, dtype=np.float32)
            arr = np.concatenate([arr, pad])
        else:
            arr = arr[:expected_dim]
    arr = arr.reshape(1, -1).astype(np.float32)
    out = sess.run(None, {name: arr})
    # take first scalar of first output
    raw = np.array(out[0]).ravel()[0]
    return float(raw)


def grid_search_temperature_bias(raws, labels, temps, biases):
    labels = np.array(labels, dtype=np.float32)
    raws = np.array(raws, dtype=np.float32)
    best = None
    best_loss = float("inf")
    for t in temps:
        for b in biases:
            ps = sigmoid((raws + b) / (t if t != 0 else 1e-12))
            eps = 1e-12
            loss = -np.mean(labels * np.log(ps + eps) + (1 - labels) * np.log(1 - ps + eps))
            if loss < best_loss:
                best_loss = loss
                best = (t, b, loss)
    return best


def main():
    model_path = os.path.join("out", "models", "model.onnx")
    print("Loading model:", model_path)
    sess = load_model(model_path)

    # Small set of labeled examples (hand-crafted, lightweight)
    labeled = [
        # benign: short low-byte flows
        {"flows": [{"bytes": 40, "duration": 0.01, "dst_port": 80}] * 5, "label": 0},
        {"flows": [{"bytes": 120, "duration": 0.02, "dst_port": 443}] * 8, "label": 0},
        {"flows": [{"bytes": 200, "duration": 0.05, "dst_port": 53}] * 4, "label": 0},
        # malicious: large byte counts, varied ports
        {"flows": [{"bytes": 5000, "duration": 1.2, "dst_port": 4444}, {"bytes": 4000, "duration": 0.8, "dst_port": 5555}], "label": 1},
        {"flows": [{"bytes": 10000, "duration": 2.5, "dst_port": 80}, {"bytes": 8000, "duration": 1.9, "dst_port": 8080}, {"bytes": 9000, "duration": 2.0, "dst_port": 22}], "label": 1},
        {"flows": [{"bytes": 3000, "duration": 0.5, "dst_port": 9999}] * 6, "label": 1},
    ]

    raws = []
    labels = []
    for s in labeled:
        fv = build_feature_vector_from_flows(s["flows"])
        raw = run_on_model(sess, fv)
        raws.append(raw)
        labels.append(float(s["label"]))
        print(f"sample label={s['label']} raw_logit={raw}")

    temps = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0, 500.0, 1000.0]
    biases = list(np.linspace(-10.0, 10.0, 41))

    print("Running grid search over temps and biases...")
    best = grid_search_temperature_bias(raws, labels, temps, biases)
    if best:
        best_temp, best_bias, best_loss = best
        out = {
            "temperature": float(best_temp),
            "bias": float(best_bias),
            "nll": float(best_loss),
            "sample_count": len(labels),
        }
        os.makedirs(os.path.join("out", "models"), exist_ok=True)
        with open(os.path.join("out", "models", "calibration_labeled.json"), "w") as fh:
            json.dump(out, fh, indent=2)
        print("Best calibration:", out)
    else:
        print("No best found")


if __name__ == "__main__":
    main()
