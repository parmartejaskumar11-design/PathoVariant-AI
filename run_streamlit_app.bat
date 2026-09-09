@echo off
title PathoVariant-AI - Streamlit Launcher
echo ====================================================================
echo   PathoVariant-AI: Launching Streamlit ML Analytics Dashboard
echo ====================================================================
echo.
echo Starting Streamlit app on http://localhost:8501...
start "PathoVariant Streamlit App" cmd /k "streamlit run streamlit_app.py"

echo ====================================================================
echo   Streamlit App launched at http://localhost:8501
echo ====================================================================
