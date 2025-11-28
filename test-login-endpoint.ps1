# Test the login endpoint
Write-Host "Testing /api/v1/test/login endpoint..." -ForegroundColor Cyan

$body = @{
    phone = "+919876543210"
    role = "consumer"
} | ConvertTo-Json

Write-Host "Request body: $body" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/test/login" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    Write-Host "`n✅ Login successful!" -ForegroundColor Green
    Write-Host "Access Token: $($response.access_token.Substring(0, 50))..." -ForegroundColor Green
    Write-Host "User: $($response.user.email) ($($response.user.role))" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Login failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Yellow
    }
}
