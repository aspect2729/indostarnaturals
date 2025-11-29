# Test Redis Cloud Connection
# Quick script to verify your Redis URL works

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  Redis Cloud Connection Test" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Prompt for Redis URL
Write-Host "Enter your Redis Cloud URL:" -ForegroundColor Yellow
Write-Host "Format: redis://default:PASSWORD@HOST:PORT" -ForegroundColor Gray
Write-Host ""
Write-Host "Example:" -ForegroundColor Gray
Write-Host "redis://default:abc123@redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com:12345" -ForegroundColor Gray
Write-Host ""

$redisUrl = Read-Host "Redis URL"

if ([string]::IsNullOrWhiteSpace($redisUrl)) {
    Write-Host ""
    Write-Host "❌ No URL provided!" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Testing connection..." -ForegroundColor Yellow
Write-Host ""

# Run Python test script
python test-redis-cloud.py "$redisUrl"

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "=====================================================================" -ForegroundColor Green
    Write-Host "  ✅ SUCCESS! Redis is working!" -ForegroundColor Green
    Write-Host "=====================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Go to Render Dashboard" -ForegroundColor White
    Write-Host "2. Select your Backend Service" -ForegroundColor White
    Write-Host "3. Go to Environment tab" -ForegroundColor White
    Write-Host "4. Add: REDIS_URL = <your_url>" -ForegroundColor White
    Write-Host "5. Save and wait for redeploy" -ForegroundColor White
} else {
    Write-Host "=====================================================================" -ForegroundColor Red
    Write-Host "  ❌ Connection failed" -ForegroundColor Red
    Write-Host "=====================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the error messages above for troubleshooting tips" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
