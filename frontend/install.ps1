# Frontend Installation Script
# Run this from the frontend directory

Write-Host "🚀 Installing Stock Intelligence Copilot Frontend..." -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
$nodeVersion = node --version 2>$null
if (-not $nodeVersion) {
    Write-Host "❌ Node.js is not installed. Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Node.js version: $nodeVersion" -ForegroundColor Green

# Check if npm is available
$npmVersion = npm --version 2>$null
if (-not $npmVersion) {
    Write-Host "❌ npm is not installed" -ForegroundColor Red
    exit 1
}

Write-Host "✓ npm version: $npmVersion" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Installation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Quick Start:" -ForegroundColor Cyan
Write-Host "   npm run dev     - Start development server (http://localhost:3000)" -ForegroundColor White
Write-Host "   npm run build   - Build for production" -ForegroundColor White
Write-Host "   npm start       - Start production server" -ForegroundColor White
Write-Host ""
Write-Host "🎨 Demo Page:" -ForegroundColor Cyan
Write-Host "   http://localhost:3000/demo" -ForegroundColor White
Write-Host ""
