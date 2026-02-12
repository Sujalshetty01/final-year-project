# Release Draft — v1.0.0

Release: v1.0.0
Date: 2026-02-13

Summary
-------
This release packages the first stable release of the GNN-based malware classification project. It includes the API server, model inference support (ONNX), Docker packaging and CI, documentation, and a reproduced IEEE-style paper PDF.

Highlights
----------
- Customized Swagger UI with dark theme, logo and favicon.
- ONNX runtime support with model health checks and smoke inference.
- Dockerfile with HEALTHCHECK; GitHub Actions CI that builds and tests the container.
- Developer helpers: `Makefile`, `scripts/setup.ps1`, `scripts/smoke_test.py`.
- Tests: unit tests and integration tests; CI will run smoke tests, lint, pytest, and Docker integration tests.
- Documentation: `docs/API.md`, `docs/PROJECT_SUMMARY.md`, `docs/PROJECT_SUMMARY_BRIEF.md`.
- Paper: `paper/ieee_paper_main.pdf` (generated and included in repo).

Assets to attach
----------------
- `paper/ieee_paper_main.pdf` — final paper PDF
- `paper/build.log` — LaTeX build transcript
- `out/models/model.onnx` (if available) — example model (not included by default)

Publishing instructions
-----------------------
Option A (web UI):
1. Go to the repository Releases page on GitHub.
2. Click "Draft a new release".
3. Tag version: `v1.0.0`, title: `v1.0.0`.
4. Paste the contents of this file into the release notes.
5. Attach assets: `paper/ieee_paper_main.pdf` and `paper/build.log` (if desired).
6. Publish the release.

Option B (gh CLI):
```bash
# create release and upload assets (requires gh installed and authenticated)
gh release create v1.0.0 \
  --title "v1.0.0" \
  --notes-file RELEASE_DRAFT.md \
  paper/ieee_paper_main.pdf \
  paper/build.log
```

Option C (curl + PAT): use the GitHub Releases API to create a release and upload assets. This requires a Personal Access Token with `repo` scope; see the GitHub docs for details.

Notes
-----
- If `out/models/model.onnx` is large or sensitive, host it externally (S3) and link it from the release notes instead of attaching to GitHub.
- The CI workflow uploads smoke and integration results as artifacts; link to CI run from the release if needed.
