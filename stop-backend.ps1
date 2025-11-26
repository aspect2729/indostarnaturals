# Stop Backend Development Server
# This script stops Redis in WSL

Write-Host "Stopping Redis in WSL..." -ForegroundColor Yellow
wsl bash -c "pkill redis-server"
Write-Host "Redis stopped!" -ForegroundColor Green
