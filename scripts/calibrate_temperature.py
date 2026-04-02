#!/usr/bin/env python3
"""Simple temperature calibration for ONNX model outputs.

Generates synthetic benign/malicious feature vectors (matching backend feature
construction), obtains raw model logits, and finds a temperature that minimizes
negative log-likelihood on the synthetic labels using a grid search.

Outputs a recommended temperature to stdout and writes `out/models/calibration.json`.
"""
import os
import json
import math
import numpy as np
try:
    import onnxruntime as ort
except Exception:
    ort = None


def build_feats_from_stats(total_bytes, count, avg_duration, distinct_ports):
    f_total_bytes = math.log(total_bytes + 1.0)
    f_total_count = math.log(count + 1.0)
    f_avg_dur = math.log(avg_duration + 1.0)
    f_dist_ports = math.log(distinct_ports + 1.0)
    mean_bytes = total_bytes / (count + 1e-6)
    f_mean_bytes = math.log(mean_bytes + 1.0)
    return np.array([f_total_bytes, f_total_count, f_avg_dur, f_dist_ports, f_mean_bytes], dtype=np.float32)


def make_input_tensor_from_feats(feats, inp_shape):
    x = np.zeros(tuple(inp_shape), dtype=np.float32)
    flat = x.ravel()
    for i, v in enumerate(feats):
        if i < flat.size:
            flat[i] = float(v)
    return x


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def softmax(x):
    e = np.exp(x - np.max(x))
    return e / e.sum()


def main():
    model_path = os.environ.get("MODEL_PATH", "out/models/model.onnx")
    if ort is None:
        raise SystemExit("onnxruntime not installed in environment")
    if not os.path.exists(model_path):
        raise SystemExit(f"Model not found: {model_path}")

    sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    inp = sess.get_inputs()[0]
    inp_shape = []
    for d in inp.shape:
        if isinstance(d, str) or d is None:
            inp_shape.append(1)
        else:
            inp_shape.append(max(1, int(d)))

    # synthesize dataset
    N = 300
    X_logits = []
    y = []

    rng = np.random.default_rng(12345)

    # benign samples
    for _ in range(N // 2):
        total_bytes = float(rng.lognormal(mean=6.0, sigma=0.5))  # modest
        count = float(rng.integers(1, 6))
        avg_duration = float(rng.lognormal(mean=0.5, sigma=0.5))
        distinct_ports = float(rng.integers(1, 3))
        feats = build_feats_from_stats(total_bytes, count, avg_duration, distinct_ports)
        x = make_input_tensor_from_feats(feats, inp_shape)
        feed = {inp.name: x}
        out = sess.run(None, feed)
        arr = np.asarray(out[0]).ravel()
        X_logits.append(arr.copy())
        y.append(0)

    # malicious samples
    for _ in range(N // 2):
        total_bytes = float(rng.lognormal(mean=12.0, sigma=1.0))  # large
        count = float(rng.integers(8, 80))
        avg_duration = float(rng.lognormal(mean=3.0, sigma=1.0))
        distinct_ports = float(rng.integers(5, 40))
        feats = build_feats_from_stats(total_bytes, count, avg_duration, distinct_ports)
        x = make_input_tensor_from_feats(feats, inp_shape)
        feed = {inp.name: x}
        out = sess.run(None, feed)
        arr = np.asarray(out[0]).ravel()
        X_logits.append(arr.copy())
        y.append(1)

    X_logits = np.stack(X_logits)
    y = np.array(y)

    # Determine whether model returns single logit or multi
    sample_arr = X_logits[0].ravel()
    single = sample_arr.size == 1

    temps = np.logspace(-3, 3, 201)
    best_t = 1.0
    best_nll = float('inf')

    for t in temps:
        if single:
            probs = sigmoid(X_logits.ravel() / t)
            probs = probs.reshape(-1)
            # clamp
            probs = np.clip(probs, 1e-12, 1.0 - 1e-12)
            nll = -np.mean(y * np.log(probs) + (1 - y) * np.log(1 - probs))
        else:
            # multi-logit: compute softmax over last dim and take class 1 prob if exists
            probs = []
            for arr in X_logits:
                p = softmax(arr.astype(np.float64) / t)
                if p.size > 1:
                    probs.append(p[1])
                else:
                    probs.append(p[0])
            probs = np.array(probs)
            probs = np.clip(probs, 1e-12, 1.0 - 1e-12)
            nll = -np.mean(y * np.log(probs) + (1 - y) * np.log(1 - probs))
        if nll < best_nll:
            best_nll = nll
            best_t = float(t)

    result = {"temperature": best_t, "nll": float(best_nll), "sample_count": int(N)}
    out_path = "out/models/calibration.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result))


if __name__ == "__main__":
    main()
