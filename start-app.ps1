# IndoStar Naturals - Complete Application Startup Script
Write-Host "========================================" -ForegroundColor Green
Write-Host "IndoStar Naturals - Starting Application" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if PostgreSQL is running
Write-Host "Checking PostgreSQL..." -ForegroundColor Yellow
$pgProcess = Get-Process -Name postgres -ErrorAction SilentlyContinue
if (-not $pgProcess) {
    Write-Host "ERROR: PostgreSQL is not running!" -ForegroundColor Red
    Write-Host "Please start PostgreSQL first." -ForegroundColor Red
    exit 1
}
Write-Host "✓ PostgreSQL is running" -ForegroundColor Green
Write-Host ""

# Check if Redis is running
Write-Host "Checking Redis..." -ForegroundColor Yellow
$redisProcess = Get-Process -Name redis-server -ErrorAction SilentlyContinue
if (-not $redisProcess) {
    Write-Host "WARNING: Redis is not running!" -ForegroundColor Yellow
    Write-Host "Some features (caching, background tasks) may not work." -ForegroundColor Yellow
} else {
    Write-Host "✓ Redis is running" -ForegroundColor Green
}
Write-Host ""

# Start Backend
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; uvicorn app.main:app --reload" -WindowStyle Normal
Write-Host "✓ Backend starting on http://localhost:8000" -ForegroundColor Green
Write-Host ""

# Wait a bit for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host ""

# Start Frontend
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev" -WindowStyle Normal
Write-Host "✓ Frontend starting on http://localhost:5173" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "Application Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
