# Changelog

All notable changes to this project are documented in this file.

## v1.0.0 - 2026-02-13

### Highlights
- Added customized Swagger UI with dark theme, branding, favicon, and logo.
- Implemented ONNX runtime support for model inference with safe fallbacks.
- Added Dockerfile with HEALTHCHECK and CI integration to build and test the container.
- Added smoke-test utilities (`scripts/smoke_test.py`) and local setup helpers (`Makefile`, `scripts/setup.ps1`).
- Expanded LaTeX paper (`paper/ieee_paper.tex`) and regenerated `paper/ieee_paper_main.pdf`.
- Added API and deployment documentation (`docs/API.md`) and project summaries (`docs/PROJECT_SUMMARY.md`, `docs/PROJECT_SUMMARY_BRIEF.md`).
- Added tests: unit tests and integration tests; CI runs smoke tests, lint, pytest, and Docker integration tests.

### Other
- Miscellaneous fixes for LaTeX build automation and PowerShell helper scripts.
