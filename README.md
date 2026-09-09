# PathoVariant-AI

Autonomous Pathogen Mutation & AI Functional Impact Analyzer.

Upload or paste DNA/RNA sequence data in FASTA format and get AI-powered classification into **Benign**, **Moderate Risk**, or **High-Risk Variant** categories.

## Features

- **Pathogen Analysis** — hybrid AI engine (biology-informed heuristics blended with a RandomForest) classifies each sequence into three risk tiers with confidence scores and interpretable subscores.
- **Batch Analysis** — analyze up to 20 FASTA files in one request with a per-file summary.
- **Rich dashboard** — Recharts visualizations (GC distribution, risk pie, nucleotide composition), CSV export, dark/light mode, glass-morphism UI.
- **Persistent AI model** — trained on labeled data and persisted with joblib; auto-reloaded on startup (no retraining on every boot).

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, FastAPI, Biopython, scikit-learn, joblib |
| Frontend | React 18, Vite, Tailwind CSS, Recharts, Lucide |

## Project Structure

```
PathoVariant-AI/
  backend/
    main.py                 # FastAPI entry point (4 endpoints)
    requirements.txt
    src/
      parser.py             # FASTA parsing (Biopython)
      ai_engine.py          # K-mer + RandomForest risk engine (persistable)
      __init__.py
    data/                   # Sample sequences; models persist here
    tests/                  # pytest suite
  frontend/
    src/
      App.jsx               # Analysis dashboard
      components/           # Navbar, FileUploader, MetricsCard, Charts
  Dockerfile
  docker-compose.yml
```

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs are at http://localhost:8000/docs.

### Frontend

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173 (proxies /api -> :8000)
```

### Optional: Real training data

Place labeled FASTA files in `backend/data/training/`. The label is parsed from the header:

```
>gene_high_NC_…        # -> High-Risk Variant
>gene_benign_…         # -> Benign Strain
>gene_moderate_…       # -> Moderate Risk
```

If no training data is present, the engine falls back to synthetic sequence generation. The trained model is persisted to `backend/data/pathogen_model.joblib` with `joblib` and automatically reloaded on startup, avoiding retraining on every boot.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health + engine state |
| GET | `/api/model-info` | Model configuration |
| POST | `/api/analyze` | Classify FASTA upload (max 50 MB) |
| POST | `/api/analyze-batch` | Classify multiple FASTA files (max 20) |

All `/api/analyze*` endpoints are rate-limited to 30 requests/min/IP by default.

## Tests

```bash
cd backend
pytest -q          # 25 tests
cd frontend
npm test           # 3 Vitest tests
```

## Docker

```bash
docker-compose up --build        # backend on :8000, frontend served on :3000
```

## Disclaimer

Research/educational tool for pathogen sequence analysis. AI classifications are heuristic estimates and must be validated by qualified bioinformaticians and clinicians before use in clinical or public-health decisions.