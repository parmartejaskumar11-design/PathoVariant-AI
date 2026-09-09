Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "  PathoVariant-AI: Launching React + FastAPI Modern Dashboard" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"
Write-Host "React Dashboard launched at http://localhost:5173" -ForegroundColor Green
