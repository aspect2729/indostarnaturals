# Start Redis Server
# This script helps you start Redis on Windows

Write-Host "🚀 Starting Redis Server..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker is available
$dockerAvailable = Get-Command docker -ErrorAction SilentlyContinue

if ($dockerAvailable) {
    Write-Host "✅ Docker found! Starting Redis in Docker..." -ForegroundColor Green
    
    # Check if redis container already exists
    $existingContainer = docker ps -a --filter "name=redis" --format "{{.Names}}"
    
    if ($existingContainer -eq "redis") {
        Write-Host "📦 Redis container already exists" -ForegroundColor Yellow
        
        # Check if it's running
        $runningContainer = docker ps --filter "name=redis" --format "{{.Names}}"
        
        if ($runningContainer -eq "redis") {
            Write-Host "✅ Redis is already running!" -ForegroundColor Green
        } else {
            Write-Host "🔄 Starting existing Redis container..." -ForegroundColor Cyan
            docker start redis
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Redis started successfully!" -ForegroundColor Green
            } else {
                Write-Host "❌ Failed to start Redis container" -ForegroundColor Red
                exit 1
            }
        }
    } else {
        Write-Host "📦 Creating new Redis container..." -ForegroundColor Cyan
        docker run -d -p 6379:6379 --name redis redis:7-alpine
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Redis container created and started!" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to create Redis container" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host ""
    Write-Host "🔍 Verifying Redis connection..." -ForegroundColor Cyan
    Start-Sleep -Seconds 2
    
    # Test Redis connection
    $redisTest = docker exec redis redis-cli ping 2>$null
    
    if ($redisTest -eq "PONG") {
        Write-Host "✅ Redis is responding correctly!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 Redis Status:" -ForegroundColor Cyan
        docker ps --filter "name=redis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    } else {
        Write-Host "⚠️  Redis may not be ready yet. Wait a few seconds and try again." -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Docker not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Docker or use one of these alternatives:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 1: Install Docker Desktop" -ForegroundColor Cyan
    Write-Host "  Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Option 2: Use WSL (Windows Subsystem for Linux)" -ForegroundColor Cyan
    Write-Host "  Run: wsl" -ForegroundColor Gray
    Write-Host "  Then: sudo service redis-server start" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Option 3: Install Redis for Windows" -ForegroundColor Cyan
    Write-Host "  Download from: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Gray
    Write-Host "  Then run: redis-server" -ForegroundColor Gray
    Write-Host ""
    Write-Host "See REDIS_SETUP_GUIDE.md for detailed instructions" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "✨ Redis is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Test Twilio OTP: cd backend && python test_twilio_otp.py +919876543210" -ForegroundColor Gray
Write-Host "  2. Start backend: cd backend && python -m uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop Redis:" -ForegroundColor Cyan
Write-Host "  docker stop redis" -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
