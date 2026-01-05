# Stock Intelligence Copilot - Quick Start Script
# Run this script to set up and test the MVP

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Stock Intelligence Copilot" -ForegroundColor Cyan
Write-Host "Quick Start Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = & python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.11 or higher from https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Check if virtual environment exists
$venvPath = "venv"
if (-Not (Test-Path $venvPath)) {
    Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "`nVirtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "Dependencies installed" -ForegroundColor Green

# Run component tests
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "Running Component Tests" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

python test_mvp.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: Tests failed. Please check the output above." -ForegroundColor Red
    exit 1
}

# Ask if user wants to start the server
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$response = Read-Host "Would you like to start the API server now? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "`nStarting API server..." -ForegroundColor Yellow
    Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Green
    Write-Host "Documentation at: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "`nPress Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    
    cd backend
    python main.py
} else {
    Write-Host "`nTo start the server later, run:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor White
    Write-Host "  python main.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Then visit: http://localhost:8000/docs" -ForegroundColor Green
}
