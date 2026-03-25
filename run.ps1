param(
    [switch]$Test
)

$ErrorActionPreference = "Stop"

function Resolve-Python {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) { return @("py", "-3") }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) { return @("python") }

    $python3Cmd = Get-Command python3 -ErrorAction SilentlyContinue
    if ($python3Cmd) { return @("python3") }

    Write-Error "Python not found. Install Python 3.12+ and ensure it's on PATH."
}

$pythonArgs = Resolve-Python

if ($Test) {
    Write-Host "Running quick endpoint tests (Flask test client)..."
    Write-Host "Installing dependencies..."
    & $pythonArgs[0] @($pythonArgs[1..($pythonArgs.Length-1)]) -m pip install -r "requirements.txt"

    & $pythonArgs[0] @($pythonArgs[1..($pythonArgs.Length-1)]) -c "from app import app as flask_app; c=flask_app.test_client(); r=c.get('/'); assert r.status_code==200; r2=c.get('/api/name'); assert r2.status_code==200; j=r2.get_json(); assert 'name' in j and isinstance(j['name'], str) and j['name'].strip(); r3=c.get('/picrewlogo.png'); assert r3.status_code==200; print('OK:', j['name'])"
    exit 0
}

Write-Host "Installing dependencies..."
& $pythonArgs[0] @($pythonArgs[1..($pythonArgs.Length-1)]) -m pip install -r "requirements.txt"

Write-Host "Starting app at http://127.0.0.1:5000 ..."
& $pythonArgs[0] @($pythonArgs[1..($pythonArgs.Length-1)]) "app.py"
