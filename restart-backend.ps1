# Restart Backend Server
Write-Host "Restarting backend server..." -ForegroundColor Cyan

# Check if Redis is running
Write-Host "Checking Redis..." -ForegroundColor Yellow
$redisCheck = Test-NetConnection -ComputerName localhost -Port 6379 -WarningAction SilentlyContinue

if (-not $redisCheck.TcpTestSucceeded) {
    Write-Host "❌ Redis is not running. Starting Redis first..." -ForegroundColor Red
    docker start indostar_redis
    Start-Sleep -Seconds 2
}

Write-Host "✅ Redis is running" -ForegroundColor Green

# Find and stop any running uvicorn processes
Write-Host "Stopping existing backend processes..." -ForegroundColor Yellow
$uvicornProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*app.main*"
}

if ($uvicornProcesses) {
    $uvicornProcesses | Stop-Process -Force
    Write-Host "Stopped existing backend processes" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "No existing backend processes found" -ForegroundColor Yellow
}

# Start the backend
Write-Host "Starting backend server..." -ForegroundColor Cyan
& .\start-backend.ps1
