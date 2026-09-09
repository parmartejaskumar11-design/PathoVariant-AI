Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "  PathoVariant-AI: Launching BOTH User Interfaces for Recruiter Review" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run streamlit_app.py"

Start-Sleep -Seconds 4
Start-Process "http://localhost:5173"
Start-Process "http://localhost:8501"

Write-Host "Both User Interfaces are now live:" -ForegroundColor Green
Write-Host "  - React Dashboard:    http://localhost:5173" -ForegroundColor Yellow
Write-Host "  - Streamlit ML App:   http://localhost:8501" -ForegroundColor Yellow
Write-Host "  - FastAPI Swagger:    http://localhost:8000/docs" -ForegroundColor Yellow
