@echo off
title PathoVariant-AI - Dual UI Launcher
echo ====================================================================
echo   PathoVariant-AI: Launching BOTH User Interfaces for Recruiter Review
echo ====================================================================
echo.
echo [1/3] Starting FastAPI Backend on http://localhost:8000...
start "PathoVariant Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --port 8000"

echo [2/3] Starting React + Vite UI on http://localhost:5173...
start "PathoVariant React UI" cmd /k "cd frontend && npm run dev"

echo [3/3] Starting Streamlit ML App on http://localhost:8501...
start "PathoVariant Streamlit App" cmd /k "streamlit run streamlit_app.py"

echo.
echo Waiting for services to initialize...
timeout /t 4 /nobreak >nul
start http://localhost:5173
start http://localhost:8501
echo ====================================================================
echo   Both UIs are now active:
echo   - React Modern UI:    http://localhost:5173
echo   - Streamlit ML App:   http://localhost:8501
echo   - FastAPI API Docs:   http://localhost:8000/docs
echo ====================================================================
