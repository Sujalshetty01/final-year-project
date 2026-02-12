Requirements & installing PyTorch (CPU/GPU)

This document explains how to install the project dependencies and provides CPU-friendly instructions for PyTorch.

Install core deps (lightweight):

```powershell
pip install -r requirements-cpu.txt
```

Install PyTorch (CPU-only):

Use the official PyTorch CPU wheels from the PyTorch index. Example (Windows / Linux):

```powershell
pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio
```

If you want GPU support (CUDA), follow the official selector at https://pytorch.org/get-started/locally/ and use the recommended command (it will point at the correct CUDA-enabled wheel index).

Notes on `torch-geometric` and related packages:

- `torch-geometric` often requires platform-specific binaries and a matching PyTorch version. Install it using the official instructions at https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html after installing PyTorch.

- If you need a reproducible environment for CI or experiments, pin exact versions and use a platform-specific wheel repository (or build via `pip wheel`).

Troubleshooting:

- If `pip install` fails for `torch` with a "no matching distribution" error, ensure you're using a supported Python version and the appropriate wheel index (CPU vs GPU).
- For offline or air-gapped installs, build wheels on a compatible machine and copy them into the environment.
