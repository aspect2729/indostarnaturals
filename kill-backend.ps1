# Kill all backend processes
Write-Host "Killing backend processes..." -ForegroundColor Yellow

# Find processes using port 8000
$processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess -Unique

if ($processes) {
    foreach ($pid in $processes) {
        try {
            $process = Get-Process -Id $pid -ErrorAction Stop
            Write-Host "Killing process: $($process.Name) (PID: $pid)" -ForegroundColor Cyan
            Stop-Process -Id $pid -Force
        } catch {
            Write-Host "Process $pid already terminated" -ForegroundColor Gray
        }
    }
    Write-Host "✅ Backend processes killed" -ForegroundColor Green
} else {
    Write-Host "No backend processes found on port 8000" -ForegroundColor Yellow
}
