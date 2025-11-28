# Start Backend Development Server
# This script starts Redis via Docker and the FastAPI backend

Write-Host "Starting Indostar Naturals Backend..." -ForegroundColor Green

# Check if Redis is running
Write-Host "`nChecking Redis..." -ForegroundColor Yellow
$redisCheck = Test-NetConnection -ComputerName localhost -Port 6379 -WarningAction SilentlyContinue

if (-not $redisCheck.TcpTestSucceeded) {
    Write-Host "Starting Redis via Docker..." -ForegroundColor Yellow
    
    # Check if container exists
    $containerExists = docker ps -a --filter "name=indostar_redis" --format "{{.Names}}"
    
    if ($containerExists) {
        docker start indostar_redis | Out-Null
    } else {
        docker run -d -p 6379:6379 --name indostar_redis redis:7-alpine | Out-Null
    }
    
    Start-Sleep -Seconds 2
    Write-Host "Redis started!" -ForegroundColor Green
} else {
    Write-Host "Redis is already running!" -ForegroundColor Green
}

# Start FastAPI server
Write-Host "`nStarting FastAPI server on http://localhost:8000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Cyan

# Change to backend directory and run uvicorn
Push-Location backend
try {
    & .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} finally {
    Pop-Location
}
