# Check if Redis is running
Write-Host "Checking Redis status..." -ForegroundColor Cyan

# Try to connect to Redis
try {
    $response = Test-NetConnection -ComputerName localhost -Port 6379 -WarningAction SilentlyContinue
    
    if ($response.TcpTestSucceeded) {
        Write-Host "✅ Redis is running on port 6379" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ Redis is NOT running on port 6379" -ForegroundColor Red
        Write-Host ""
        Write-Host "To start Redis, you have two options:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Option 1: Using Docker (Recommended)" -ForegroundColor Cyan
        Write-Host "  1. Start Docker Desktop"
        Write-Host "  2. Run: docker run -d -p 6379:6379 --name indostar_redis redis:7-alpine"
        Write-Host ""
        Write-Host "Option 2: Using Docker Compose" -ForegroundColor Cyan
        Write-Host "  1. Start Docker Desktop"
        Write-Host "  2. Run: docker-compose up redis -d"
        Write-Host ""
        Write-Host "For more details, see REDIS_SETUP_GUIDE.md" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Error checking Redis: $_" -ForegroundColor Red
    exit 1
}
