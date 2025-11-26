# PostgreSQL Setup Script for Indostar Naturals

Write-Host "PostgreSQL Setup for Indostar Naturals E-commerce" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""

# Add PostgreSQL to PATH
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"

# Prompt for password
$password = Read-Host "Enter your PostgreSQL postgres user password" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
$plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Set environment variable
$env:PGPASSWORD = $plainPassword

Write-Host ""
Write-Host "Creating databases..." -ForegroundColor Yellow

# Create main database
try {
    psql -U postgres -h localhost -c "CREATE DATABASE indostar_naturals;" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Created database: indostar_naturals" -ForegroundColor Green
    } else {
        Write-Host "Database indostar_naturals may already exist or password is incorrect" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error creating indostar_naturals database" -ForegroundColor Red
}

# Create test database
try {
    psql -U postgres -h localhost -c "CREATE DATABASE indostar_naturals_test;" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Created database: indostar_naturals_test" -ForegroundColor Green
    } else {
        Write-Host "Database indostar_naturals_test may already exist" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error creating indostar_naturals_test database" -ForegroundColor Red
}

Write-Host ""
Write-Host "Verifying databases..." -ForegroundColor Yellow
psql -U postgres -h localhost -c "\l" | Select-String "indostar"

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update backend/.env with your PostgreSQL password"
Write-Host "2. Run: cd backend"
Write-Host "3. Run: python -m venv venv"
Write-Host "4. Run: .\venv\Scripts\Activate.ps1"
Write-Host "5. Run: pip install -r requirements.txt"
Write-Host "6. Run: alembic upgrade head"
Write-Host "7. Run: uvicorn app.main:app --reload"
