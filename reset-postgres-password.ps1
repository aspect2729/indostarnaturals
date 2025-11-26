# PostgreSQL Password Reset Script
# Run this as Administrator

Write-Host "PostgreSQL Password Reset Tool" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Detect PostgreSQL version
$pgVersions = Get-ChildItem "C:\Program Files\PostgreSQL" -Directory | Select-Object -ExpandProperty Name
Write-Host "Found PostgreSQL versions: $($pgVersions -join ', ')" -ForegroundColor Cyan

# Use the latest version
$pgVersion = ($pgVersions | Sort-Object -Descending)[0]
Write-Host "Using PostgreSQL version: $pgVersion" -ForegroundColor Green
Write-Host ""

$pgDataDir = "C:\Program Files\PostgreSQL\$pgVersion\data"
$pgHbaFile = "$pgDataDir\pg_hba.conf"
$pgBinDir = "C:\Program Files\PostgreSQL\$pgVersion\bin"
$serviceName = "postgresql-x64-$pgVersion"

# Check if service exists
$service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if (-not $service) {
    Write-Host "ERROR: PostgreSQL service '$serviceName' not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Backing up pg_hba.conf..." -ForegroundColor Yellow
Copy-Item $pgHbaFile "$pgHbaFile.backup" -Force
Write-Host "[OK] Backup created" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Modifying authentication to 'trust'..." -ForegroundColor Yellow
(Get-Content $pgHbaFile) -replace 'scram-sha-256', 'trust' -replace 'md5', 'trust' | Set-Content $pgHbaFile
Write-Host "[OK] Authentication modified" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Restarting PostgreSQL service..." -ForegroundColor Yellow
Restart-Service $serviceName
Start-Sleep -Seconds 3
Write-Host "[OK] Service restarted" -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Changing password to 'postgres'..." -ForegroundColor Yellow
$psqlPath = "$pgBinDir\psql.exe"
& $psqlPath -U postgres -h localhost -c "ALTER USER postgres PASSWORD 'postgres';" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Password changed successfully" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Password change may have failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 5: Restoring authentication..." -ForegroundColor Yellow
Move-Item "$pgHbaFile.backup" $pgHbaFile -Force
Write-Host "[OK] Authentication restored" -ForegroundColor Green

Write-Host ""
Write-Host "Step 6: Restarting PostgreSQL service..." -ForegroundColor Yellow
Restart-Service $serviceName
Start-Sleep -Seconds 3
Write-Host "[OK] Service restarted" -ForegroundColor Green

Write-Host ""
Write-Host "Step 7: Testing connection..." -ForegroundColor Yellow
$env:PGPASSWORD = "postgres"
& $psqlPath -U postgres -h localhost -c "SELECT version();" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Connection successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "SUCCESS! Your PostgreSQL password is now: postgres" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run: .\setup-postgres.ps1" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Connection failed. Please check the error above." -ForegroundColor Red
}
