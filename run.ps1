param(
    [switch]$Test
)

$ErrorActionPreference = "Stop"

$python = Join-Path $env:LocalAppData "Programs\Python\Python312\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Python executable not found at $python. Install Python first."
}

if ($Test) {
    Write-Host "Running quick endpoint tests..."
    $homeStatus = curl.exe -s -o NUL -w "%{http_code}" "http://127.0.0.1:5000/"
    $apiBody = curl.exe -s "http://127.0.0.1:5000/api/name"

    Write-Host "GET / status: $homeStatus"
    Write-Host "GET /api/name response:"
    Write-Host $apiBody
    exit 0
}

Write-Host "Installing dependencies..."
& $python -m pip install -r "requirements.txt"

Write-Host "Starting app at http://127.0.0.1:5000 ..."
& $python "app.py"
