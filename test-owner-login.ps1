# Test Owner Login Flow
Write-Host "Testing Owner Login Flow..." -ForegroundColor Cyan
Write-Host ""

$phone = "+919999999999"
$backendUrl = "http://localhost:8000"

# Step 1: Request OTP
Write-Host "Step 1: Requesting OTP for $phone..." -ForegroundColor Yellow
$sendOtpResponse = Invoke-WebRequest -Uri "$backendUrl/api/auth/send-otp" `
    -Method POST `
    -ContentType "application/json" `
    -Body (@{phone=$phone} | ConvertTo-Json) `
    -UseBasicParsing

Write-Host "Response: $($sendOtpResponse.StatusCode)" -ForegroundColor Green
Write-Host "Body: $($sendOtpResponse.Content)" -ForegroundColor Gray
Write-Host ""

# Step 2: Check backend logs for OTP (in development mode)
Write-Host "Step 2: Check your backend console for the OTP code" -ForegroundColor Yellow
Write-Host "It should show: [DEV] OTP for ${phone}: XXXXXX" -ForegroundColor Gray
Write-Host ""

# Step 3: Prompt for OTP
$otp = Read-Host "Enter the OTP from backend console"

# Step 4: Verify OTP
Write-Host ""
Write-Host "Step 3: Verifying OTP..." -ForegroundColor Yellow
try {
    $verifyResponse = Invoke-WebRequest -Uri "$backendUrl/api/auth/verify-otp" `
        -Method POST `
        -ContentType "application/json" `
        -Body (@{phone=$phone; otp=$otp} | ConvertTo-Json) `
        -UseBasicParsing
    
    Write-Host "✅ Login successful!" -ForegroundColor Green
    Write-Host "Response: $($verifyResponse.Content)" -ForegroundColor Gray
    
    $tokens = $verifyResponse.Content | ConvertFrom-Json
    Write-Host ""
    Write-Host "Access Token: $($tokens.access_token.Substring(0, 50))..." -ForegroundColor Cyan
    Write-Host "User Role: $($tokens.user.role)" -ForegroundColor Cyan
    Write-Host "User Name: $($tokens.user.name)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Login failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Gray
    }
}
