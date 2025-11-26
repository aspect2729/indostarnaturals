# Start Backend in Hybrid Mode
# Uses Docker for Redis/Postgres, runs FastAPI locally

Write-Host "Starting Indostar Naturals Backend (Hybrid Mode)..." -ForegroundColor Green

# Start only Redis and Postgres via Docker
Write-Host "`nStarting Redis and PostgreSQL via Docker..." -ForegroundColor Yellow
docker-compose up -d postgres redis

Write-Host "`nWaiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Navigate to backend directory
Set-Location backend

# Activate virtual environment
Write-Host "`nActivating Python virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Start FastAPI server
Write-Host "`nStarting FastAPI server on http://localhost:8000..." -ForegroundColor Green
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Cyan

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
