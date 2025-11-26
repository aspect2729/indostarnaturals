# Check Application Status
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "IndoStar Naturals - Status Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check PostgreSQL
Write-Host "PostgreSQL:" -NoNewline
$pgProcess = Get-Process -Name postgres -ErrorAction SilentlyContinue
if ($pgProcess) {
    Write-Host " ✓ Running" -ForegroundColor Green
} else {
    Write-Host " ✗ Not Running" -ForegroundColor Red
}

# Check Redis
Write-Host "Redis:     " -NoNewline
$redisProcess = Get-Process -Name redis-server -ErrorAction SilentlyContinue
if ($redisProcess) {
    Write-Host " ✓ Running" -ForegroundColor Green
} else {
    Write-Host " ✗ Not Running" -ForegroundColor Yellow
}

# Check Backend (port 8000)
Write-Host "Backend:   " -NoNewline
$backendPort = netstat -ano | findstr :8000 | findstr LISTENING
if ($backendPort) {
    Write-Host " ✓ Running on port 8000" -ForegroundColor Green
} else {
    Write-Host " ✗ Not Running" -ForegroundColor Red
}

# Check Frontend (port 5173)
Write-Host "Frontend:  " -NoNewline
$frontendPort = netstat -ano | findstr :5173 | findstr LISTENING
if ($frontendPort) {
    Write-Host " ✓ Running on port 5173" -ForegroundColor Green
} else {
    Write-Host " ✗ Not Running" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

# Check for extra Vite servers
$extraVite = netstat -ano | findstr :5174 | findstr LISTENING
if ($extraVite) {
    Write-Host "⚠ WARNING: Extra Vite server on port 5174" -ForegroundColor Yellow
    Write-Host "  This may cause redirect issues." -ForegroundColor Yellow
    Write-Host "  Run: netstat -ano | findstr :5174" -ForegroundColor Yellow
}

Write-Host ""
