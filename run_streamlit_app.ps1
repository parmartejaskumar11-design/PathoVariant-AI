Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "  PathoVariant-AI: Launching Streamlit ML Analytics Dashboard" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run streamlit_app.py"
Start-Sleep -Seconds 3
Start-Process "http://localhost:8501"
Write-Host "Streamlit Dashboard launched at http://localhost:8501" -ForegroundColor Green
