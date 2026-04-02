#!/usr/bin/env python3
"""Run the same feature construction as the backend for the test_analyze sample
and print the raw model outputs (logits) so we can see why backend falls back.
"""
import os
import numpy as np
import math
try:
    import onnxruntime as ort
except Exception:
    raise SystemExit('onnxruntime required')


def build_features(flows, inp_shape_len=None):
    def _bytes_of(f):
        if isinstance(f.get('bytes', None), (int, float)):
            return float(f.get('bytes'))
        a = f.get('bytes_sent') or f.get('bytes_sent_total') or 0
        b = f.get('bytes_received') or f.get('bytes_recv') or 0
        try:
            return float(a) + float(b)
        except Exception:
            return 0.0

    total_bytes = float(sum((_bytes_of(f) or 0.0) for f in flows))
    total_count = float(len(flows))
    durations = []
    byte_vals = []
    ports = []
    for f in flows:
        dur = f.get('duration')
        if dur is None:
            dur = f.get('flow_duration') or f.get('time_ms') or 0
        try:
            durations.append(float(dur))
        except Exception:
            durations.append(0.0)
        try:
            b = float(f.get('bytes', None) if f.get('bytes', None) is not None else (
                (f.get('bytes_sent') or 0) + (f.get('bytes_received') or 0)
            ))
        except Exception:
            b = 0.0
        byte_vals.append(b)
        for k in ('sport', 'dport', 'src_port', 'dst_port', 'src_port_int', 'dst_port_int'):
            if k in f and f.get(k) is not None:
                ports.append(f.get(k))

    avg_duration = float(sum(durations) / len(durations)) if durations else 0.0
    distinct_ports = float(len(set(ports)))
    import math
    f_total_bytes = math.log(total_bytes + 1.0)
    f_total_count = math.log(total_count + 1.0)
    f_avg_dur = math.log(avg_duration + 1.0)
    f_dist_ports = math.log(distinct_ports + 1.0)
    mean_bytes = total_bytes / (total_count + 1e-6)
    f_mean_bytes = math.log(mean_bytes + 1.0)
    max_b = float(max(byte_vals)) if byte_vals else 0.0
    min_b = float(min(byte_vals)) if byte_vals else 0.0
    std_b = float(np.std(np.array(byte_vals, dtype=np.float32))) if byte_vals else 0.0
    f_max_b = math.log(max_b + 1.0)
    f_min_b = math.log(min_b + 1.0)
    f_std_b = math.log(std_b + 1.0)
    port_entropy = 0.0
    if ports:
        vals, counts = np.unique(np.array(ports), return_counts=True)
        probs = counts / counts.sum()
        port_entropy = float(-np.sum(probs * np.log(probs + 1e-12)))
    f_port_entropy = math.log(port_entropy + 1.0)

    feats = [f_total_bytes, f_total_count, f_avg_dur, f_dist_ports, f_mean_bytes,
             f_max_b, f_min_b, f_std_b, f_port_entropy]
    return np.array(feats, dtype=np.float32)


def main():
    model_path = os.path.join('out', 'models', 'model.onnx')
    if not os.path.exists(model_path):
        print('Model not found:', model_path)
        return
    sess = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    inp = sess.get_inputs()[0]
    print('Model input shape:', inp.shape)
    # Also inspect a small labeled set to determine which output index maps to 'malicious'
    labeled = [
        # benign
        ({'flows': [{'bytes': 40, 'duration': 0.01, 'dst_port': 80}] * 5}, 0),
        ({'flows': [{'bytes': 120, 'duration': 0.02, 'dst_port': 443}] * 8}, 0),
        ({'flows': [{'bytes': 200, 'duration': 0.05, 'dst_port': 53}] * 4}, 0),
        # malicious
        ({'flows': [{'bytes': 5000, 'duration': 1.2, 'dst_port': 4444}, {'bytes': 4000, 'duration': 0.8, 'dst_port': 5555}]}, 1),
        ({'flows': [{'bytes': 10000, 'duration': 2.5, 'dst_port': 80}, {'bytes': 8000, 'duration': 1.9, 'dst_port': 8080}, {'bytes': 9000, 'duration': 2.0, 'dst_port': 22}]}, 1),
        ({'flows': [{'bytes': 3000, 'duration': 0.5, 'dst_port': 9999}] * 6}, 1),
    ]

    expected = None
    if isinstance(inp.shape, (list, tuple)) and len(inp.shape) >= 2:
        expected = inp.shape[1]

    # inspect labeled samples
    for idx, (s, label) in enumerate(labeled):
        fv = build_features(s['flows'])
        arr = fv
        if expected is not None and expected != arr.size:
            if expected > arr.size:
                pad = np.zeros(expected - arr.size, dtype=np.float32)
                arr = np.concatenate([arr, pad])
            else:
                arr = arr[:expected]
        arr = arr.reshape(1, -1).astype(np.float32)
        outs = sess.run(None, {inp.name: arr})
        print(f'sample[{idx}] label={label} raw_outputs={ [o.tolist() if hasattr(o, "tolist") else o for o in outs] }')

    # Also print the original test_analyze sample
    sample = [
        {'bytes': 100, 'duration': 1, 'sport': 80, 'dport': 443},
        {'bytes': 2000000, 'duration': 5, 'sport': 1234, 'dport': 80}
    ]
    fv = build_features(sample)
    print('Test sample feature vector:', fv.tolist())
    arr = fv
    if expected is not None and expected != arr.size:
        if expected > arr.size:
            pad = np.zeros(expected - arr.size, dtype=np.float32)
            arr = np.concatenate([arr, pad])
        else:
            arr = arr[:expected]
    arr = arr.reshape(1, -1).astype(np.float32)
    outs = sess.run(None, {inp.name: arr})
    print('Test sample raw outputs:', [o.tolist() if hasattr(o, 'tolist') else o for o in outs])


if __name__ == '__main__':
    main()
