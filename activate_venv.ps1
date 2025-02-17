# Get the directory where the script is located
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Path to the virtual environment (assuming it's in a 'venv' folder in the same directory)
$venvPath = Join-Path $scriptPath "venv"

# Check if venv exists
if (-not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found at: $venvPath"
    Write-Host "Creating new virtual environment..."
    python -m venv $venvPath
}

# Activate the virtual environment
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
& $activateScript

# Keep the window open and start a new PowerShell session
if ($host.Name -eq 'ConsoleHost') {
    PowerShell -NoExit -Command "cd '$scriptPath'; & '$activateScript'"
}