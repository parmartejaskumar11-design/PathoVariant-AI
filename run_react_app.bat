@echo off
title PathoVariant-AI - React + FastAPI Launcher
echo ====================================================================
echo   PathoVariant-AI: Launching React + FastAPI Modern Dashboard
echo ====================================================================
echo.
echo [1/2] Starting FastAPI Backend on http://localhost:8000...
start "PathoVariant Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --port 8000"

echo [2/2] Starting React + Vite Frontend on http://localhost:5173...
start "PathoVariant Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Waiting for services to initialize...
timeout /t 3 /nobreak >nul
start http://localhost:5173
echo ====================================================================
echo   Dashboard launched at http://localhost:5173
echo ====================================================================
