# Babylon AI Gold Intelligence - Backend Startup Script
# Starts the FastAPI backend server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Babylon AI Gold Intelligence" -ForegroundColor Cyan
Write-Host "Backend Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if venv exists
if (!(Test-Path "backend\.venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    cd backend
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    cd ..
} else {
    Write-Host "Virtual environment found" -ForegroundColor Green
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
cd backend
.\.venv\Scripts\Activate.ps1

# Check if data is available
Write-Host "Checking data availability..." -ForegroundColor Yellow
if (!(Test-Path "..\BabylonAI_Gold_Data_Starter\data\demo")) {
    Write-Host "WARNING: Demo data not found" -ForegroundColor Red
    Write-Host "The system will attempt to load data at runtime" -ForegroundColor Yellow
}

# Start backend
Write-Host ""
Write-Host "Starting FastAPI backend..." -ForegroundColor Green
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python main.py
