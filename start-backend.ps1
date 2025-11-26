# Start Backend Development Server
# This script starts Redis in WSL and the FastAPI backend

Write-Host "Starting Indostar Naturals Backend..." -ForegroundColor Green

# Check if Redis is running in WSL
Write-Host "`nChecking Redis..." -ForegroundColor Yellow
$redisCheck = wsl bash -c "pgrep redis-server"

if (-not $redisCheck) {
    Write-Host "Starting Redis in WSL..." -ForegroundColor Yellow
    Start-Process wsl -ArgumentList "bash", "-c", "redis-server --daemonize yes" -NoNewWindow
    Start-Sleep -Seconds 2
    Write-Host "Redis started!" -ForegroundColor Green
} else {
    Write-Host "Redis is already running!" -ForegroundColor Green
}

# Navigate to backend directory
Set-Location backend

# Activate virtual environment
Write-Host "`nActivating Python virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Start FastAPI server
Write-Host "`nStarting FastAPI server on http://localhost:8000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Cyan

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
