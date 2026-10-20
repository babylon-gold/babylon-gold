# Babylon AI Gold Intelligence - Frontend Startup Script
# Starts the Next.js frontend development server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Babylon AI Gold Intelligence" -ForegroundColor Cyan
Write-Host "Frontend Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

cd frontend

# Check if node_modules exists
if (!(Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install --legacy-peer-deps
}

# Create .env.local
Write-Host "Setting up environment..." -ForegroundColor Yellow
if (!(Test-Path ".env.local")) {
    @"
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
"@ | Out-File -Encoding utf8 ".env.local"
    Write-Host ".env.local created" -ForegroundColor Green
}

# Start frontend
Write-Host ""
Write-Host "Starting Next.js development server..." -ForegroundColor Green
Write-Host "Dashboard will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

npm run dev
