# Project Docs

This `docs` folder contains the project summary documents for quick reference.

- Full project summary: [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)
- Brief summary: [docs/PROJECT_SUMMARY_BRIEF.md](docs/PROJECT_SUMMARY_BRIEF.md)

Quick actions

- Open the full summary: `code docs/PROJECT_SUMMARY.md`
- Open the brief summary: `code docs/PROJECT_SUMMARY_BRIEF.md`

Quick start (very brief)

1. Activate virtualenv (Windows):

```powershell
& .venv\Scripts\Activate.ps1
```

2. Install backend deps:

```powershell
pip install -r backend/requirements.txt
```

3. Generate a short sample and run smoke tests (examples):

```powershell
python data/generate_sample.py --out out/sample/
python models/train.py --data out/sample/ --epochs 5 --out out/models/quick
uvicorn backend.main:app --reload
python backend/smoke_test.py
```

Contact

- Maintainer: Sujalshetty01 (GitHub)
- Repo: https://github.com/Sujalshetty01/final-year-project
