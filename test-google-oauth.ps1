# Test Google OAuth Configuration
Write-Host "Testing Google OAuth Configuration..." -ForegroundColor Cyan
Write-Host ""

# Check frontend .env
Write-Host "1. Checking Frontend Configuration..." -ForegroundColor Yellow
$frontendEnv = Get-Content "frontend/.env" -ErrorAction SilentlyContinue
if ($frontendEnv -match "VITE_GOOGLE_CLIENT_ID=(.+)") {
    $clientId = $matches[1]
    Write-Host "   [OK] Client ID found: $($clientId.Substring(0, 20))..." -ForegroundColor Green
} else {
    Write-Host "   [FAIL] VITE_GOOGLE_CLIENT_ID not found in frontend/.env" -ForegroundColor Red
    exit 1
}

# Check backend .env
Write-Host ""
Write-Host "2. Checking Backend Configuration..." -ForegroundColor Yellow
$backendEnv = Get-Content "backend/.env" -ErrorAction SilentlyContinue
if ($backendEnv -match "GOOGLE_OAUTH_CLIENT_ID=(.+)") {
    Write-Host "   [OK] Backend Client ID configured" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] GOOGLE_OAUTH_CLIENT_ID not found in backend/.env" -ForegroundColor Red
}

if ($backendEnv -match "GOOGLE_OAUTH_CLIENT_SECRET=(.+)") {
    Write-Host "   [OK] Backend Client Secret configured" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] GOOGLE_OAUTH_CLIENT_SECRET not found in backend/.env" -ForegroundColor Red
}

# Check if servers are running
Write-Host ""
Write-Host "3. Checking if servers are running..." -ForegroundColor Yellow

$backendRunning = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($backendRunning) {
    Write-Host "   [OK] Backend is running on port 8000" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Backend is NOT running on port 8000" -ForegroundColor Red
}

$frontendRunning = Test-NetConnection -ComputerName localhost -Port 5173 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($frontendRunning) {
    Write-Host "   [OK] Frontend is running on port 5173" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Frontend is NOT running on port 5173" -ForegroundColor Red
}

# Instructions
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "GOOGLE CLOUD CONSOLE CONFIGURATION REQUIRED" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "The 403 error is from Google's servers, not your code!" -ForegroundColor White
Write-Host ""
Write-Host "To fix:" -ForegroundColor Yellow
Write-Host "  1. Go to: https://console.cloud.google.com/apis/credentials" -ForegroundColor Cyan
Write-Host "  2. Find your OAuth 2.0 Client ID and click Edit" -ForegroundColor Cyan
Write-Host "  3. Under 'Authorized JavaScript origins', add:" -ForegroundColor Cyan
Write-Host "       http://localhost:5173" -ForegroundColor White
Write-Host "       http://localhost:8000" -ForegroundColor White
Write-Host "  4. Click SAVE and wait 5-10 minutes" -ForegroundColor Cyan
Write-Host "  5. Clear browser cache or use incognito mode" -ForegroundColor Cyan
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "ALTERNATIVE: Use OTP (Phone) Authentication" -ForegroundColor Green
Write-Host "This works immediately without Google configuration!" -ForegroundColor Green
Write-Host ""
