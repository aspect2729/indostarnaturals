# Clear Python cache files
Write-Host "Clearing Python cache..." -ForegroundColor Yellow

# Remove __pycache__ directories
Get-ChildItem -Path backend -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Write-Host "Cleared __pycache__ directories" -ForegroundColor Green

# Remove .pyc files
Get-ChildItem -Path backend -Recurse -Filter "*.pyc" | Remove-Item -Force
Write-Host "Cleared .pyc files" -ForegroundColor Green

Write-Host "`nPython cache cleared! Please restart the backend server." -ForegroundColor Green
