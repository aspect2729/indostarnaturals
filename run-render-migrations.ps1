# PowerShell script to run migrations on Render via HTTP endpoint
# Usage: .\run-render-migrations.ps1

Write-Host "🔄 Running database migrations on Render..." -ForegroundColor Cyan

# Get JWT secret from backend .env file
$envFile = "backend\.env"
if (Test-Path $envFile) {
    $jwtSecret = Get-Content $envFile | Where-Object { $_ -match "^JWT_SECRET_KEY=" } | ForEach-Object { $_.Split("=")[1].Trim() }
    
    if ($jwtSecret) {
        Write-Host "✓ Found JWT_SECRET_KEY in .env file" -ForegroundColor Green
    } else {
        Write-Host "❌ JWT_SECRET_KEY not found in .env file" -ForegroundColor Red
        $jwtSecret = Read-Host "Please enter your JWT_SECRET_KEY from Render environment variables"
    }
} else {
    Write-Host "⚠️  backend\.env file not found" -ForegroundColor Yellow
    $jwtSecret = Read-Host "Please enter your JWT_SECRET_KEY from Render environment variables"
}

# Render backend URL
$renderUrl = "https://indostarnaturals.onrender.com"
Write-Host "📡 Connecting to: $renderUrl" -ForegroundColor Cyan

# Create headers
$headers = @{
    "X-Admin-Secret" = $jwtSecret
    "Content-Type" = "application/json"
}

try {
    # Run migrations
    Write-Host "`n🚀 Triggering migrations..." -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "$renderUrl/admin/run-migrations" -Method Post -Headers $headers -TimeoutSec 300
    
    Write-Host "`n✅ SUCCESS!" -ForegroundColor Green
    Write-Host "Status: $($response.status)" -ForegroundColor Green
    Write-Host "Message: $($response.message)" -ForegroundColor Green
    
    if ($response.output) {
        Write-Host "`n📋 Migration Output:" -ForegroundColor Cyan
        Write-Host $response.output -ForegroundColor Gray
    }
    
    if ($response.warning) {
        Write-Host "`n⚠️  WARNING: $($response.warning)" -ForegroundColor Yellow
    }
    
    # Verify migrations worked
    Write-Host "`n🔍 Verifying API endpoints..." -ForegroundColor Cyan
    
    try {
        $categoriesResponse = Invoke-RestMethod -Uri "$renderUrl/api/v1/categories" -Method Get -TimeoutSec 30
        Write-Host "✓ Categories endpoint working" -ForegroundColor Green
    } catch {
        Write-Host "❌ Categories endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    try {
        $productsResponse = Invoke-RestMethod -Uri "$renderUrl/api/v1/products" -Method Get -TimeoutSec 30
        Write-Host "✓ Products endpoint working" -ForegroundColor Green
    } catch {
        Write-Host "❌ Products endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "`n✅ Migrations completed successfully!" -ForegroundColor Green
    Write-Host "`n⚠️  IMPORTANT: Remember to remove the admin endpoint after deployment!" -ForegroundColor Yellow
    Write-Host "   Run: git rm backend/app/api/admin_migrations.py" -ForegroundColor Yellow
    
} catch {
    Write-Host "`n❌ FAILED!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "Status Code: $statusCode" -ForegroundColor Red
        
        if ($statusCode -eq 403) {
            Write-Host "`n💡 Tip: Check that your JWT_SECRET_KEY is correct" -ForegroundColor Yellow
            Write-Host "   Get it from: Render Dashboard → Your Service → Environment → JWT_SECRET_KEY" -ForegroundColor Yellow
        } elseif ($statusCode -eq 404) {
            Write-Host "`n💡 Tip: The admin endpoint might not be deployed yet" -ForegroundColor Yellow
            Write-Host "   1. Commit and push the new code" -ForegroundColor Yellow
            Write-Host "   2. Wait for Render to deploy (2-5 minutes)" -ForegroundColor Yellow
            Write-Host "   3. Try again" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n📖 For more help, see: RENDER_FREE_MIGRATION_GUIDE.md" -ForegroundColor Cyan
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
