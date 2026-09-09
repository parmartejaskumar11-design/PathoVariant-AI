# PathoVariant-AI

**Autonomous Pathogen Mutation & AI Functional Impact Analyzer**

[![CI](https://github.com/parmartejaskumar11-design/PathoVariant-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/parmartejaskumar11-design/PathoVariant-AI/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react)](https://react.dev)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-FF4B4B.svg?logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ⚡ 1-Click Launchers (For Recruiters & Evaluators)

This repository includes **Dual User Interfaces** tailored for both production deployment and interactive data science evaluation.

### Option 1: Run Both UIs Simultaneously (Recommended)
Double-click **`run_both_uis.bat`** (or run `./run_both_uis.ps1` in PowerShell).
- **React Modern Dashboard**: `http://localhost:5173`
- **Streamlit ML App**: `http://localhost:8501`
- **FastAPI Interactive Docs**: `http://localhost:8000/docs`

---

### Option 2: Run React + Tailwind Dashboard (Primary Production UI)
Double-click **`run_react_app.bat`** (or run `./run_react_app.ps1`).

```bash
# Manual Start:
# Terminal 1: Backend
cd backend && python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm install && npm run dev
# Open http://localhost:5173
```

---

### Option 3: Run Streamlit ML App (Interactive Analytics UI)
Double-click **`run_streamlit_app.bat`** (or run `./run_streamlit_app.ps1`).

```bash
# Manual Start:
pip install -r requirements.txt
streamlit run streamlit_app.py
# Open http://localhost:8501
```

---

## 🌟 Key Features

- **Hybrid AI Engine**: Combines transparent biological heuristics ($80\%$) with a supervised **RandomForestClassifier** ($20\%$) across $64$-dimensional 3-mer frequency embeddings.
- **Three-Tier Risk Classification**: Classifies nucleotide sequences into **High-Risk Variant**, **Moderate Risk**, and **Benign Strain** with calibrated confidence scores.
- **Deep Genomic Metrics**: Computes GC content imbalance, homopolymer slippage runs ($\ge 4$ bp), tandem repeats, nucleotide frequencies, and protein translation.
- **High-Throughput Batch Processing**: Analyze up to $20$ FASTA files concurrently with per-file statistical rollups.
- **Dual User Interfaces**:
  1. **React 18 SPA**: Glassmorphism UI, dark/light theme toggle, real-time Recharts visualizations, CSV export.
  2. **Streamlit ML App**: Plotly interactive gauges and charts, one-click pathogen sample loading (SARS-CoV-2, H5N1, Lambda Phage).
- **Model Persistence**: Automatic caching of trained models with `joblib` in `backend/data/pathogen_model.joblib`.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend API** | Python 3.13, FastAPI, Biopython, scikit-learn, joblib, Uvicorn |
| **Primary Frontend** | React 18, Vite, Tailwind CSS, Lucide React, Recharts |
| **ML Analytics App** | Streamlit, Plotly Express, Pandas, NumPy |
| **DevOps & Cloud** | Docker, Docker Compose, Nginx, GitHub Actions CI/CD |

---

## 📁 Project Architecture

```
PathoVariant-AI/
├── run_both_uis.bat          # 1-Click Dual UI launcher (React + Streamlit + FastAPI)
├── run_react_app.bat         # 1-Click React Dashboard launcher
├── run_streamlit_app.bat     # 1-Click Streamlit launcher
├── streamlit_app.py          # Streamlit Community Cloud web app
├── Dockerfile                # Multi-stage production container
├── docker-compose.yml        # Multi-container orchestration
├── requirements.txt          # Root Python dependencies
│
├── backend/
│   ├── main.py               # FastAPI application & REST endpoints
│   ├── requirements.txt      # Backend Python requirements
│   ├── src/
│   │   ├── parser.py         # Biopython FASTA parser & nucleotide profiler
│   │   └── ai_engine.py      # K-mer feature extractor & RandomForest engine
│   ├── data/                 # Sample sequences & persisted ML model
│   └── tests/                # 25 automated unit tests (pytest)
│
└── frontend/
    ├── src/
    │   ├── App.jsx           # React analysis dashboard
    │   └── components/       # Charts, FileUploader, MetricsCard, Navbar
    ├── package.json          # Node dependencies (Vite + React + Tailwind)
    └── vite.config.js        # Vite build & API reverse proxy configuration
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Healthcheck & AI engine initialization status |
| `GET` | `/api/model-info` | Feature dimensions, class centers, & hyperparameters |
| `POST` | `/api/analyze` | Single FASTA upload classification (Max 50 MB) |
| `POST` | `/api/analyze-batch` | Multi-file batch classification (Max 20 files) |

Interactive Swagger documentation is available at `http://localhost:8000/docs`.

---

## 🧪 Automated Testing

```bash
# Run Backend Tests (25 tests passing)
cd backend
python -m pytest -q

# Run Frontend Tests (3 Vitest suites passing)
cd frontend
npm test
```

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

---

## 👨‍💻 Author & Contributions

**Tejas Parmar**
- GitHub: [@parmartejaskumar11-design](https://github.com/parmartejaskumar11-design)
- Repository: [PathoVariant-AI](https://github.com/parmartejaskumar11-design/PathoVariant-AI)

*Disclaimer: PathoVariant-AI is an educational and computational genomics research tool. AI predictions provide heuristic insights and should be validated through clinical bioinformatic protocols.*
