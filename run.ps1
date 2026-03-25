param(
    [switch]$Test
)

$ErrorActionPreference = "Stop"

$python = Join-Path $env:LocalAppData "Programs\Python\Python312\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Python executable not found at $python. Install Python first."
}

if ($Test) {
    Write-Host "Running quick endpoint tests (Flask test client)..."
    Write-Host "Installing dependencies..."
    & $python -m pip install -r "requirements.txt"

    & $python -c "from app import app as flask_app; c=flask_app.test_client(); r=c.get('/'); assert r.status_code==200; r2=c.get('/api/name'); assert r2.status_code==200; j=r2.get_json(); assert 'name' in j and isinstance(j['name'], str) and j['name'].strip(); r3=c.get('/picrewlogo.png'); assert r3.status_code==200; print('OK:', j['name'])"
    exit 0
}

Write-Host "Installing dependencies..."
& $python -m pip install -r "requirements.txt"

Write-Host "Starting app at http://127.0.0.1:5000 ..."
& $python "app.py"
