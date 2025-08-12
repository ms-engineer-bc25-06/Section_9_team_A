# Bridge Line Development Setup Script for Windows
# PowerShell script for setting up the development environment

Write-Host "🚀 Bridge Line Development Environment Setup for Windows" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is available
Write-Host "Checking Docker Compose..." -ForegroundColor Yellow
try {
    docker compose version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker Compose is not available. Please update Docker Desktop." -ForegroundColor Red
    exit 1
}

# Start the environment
Write-Host ""
Write-Host "Starting Bridge Line environment..." -ForegroundColor Yellow

# Step 1: Start database services
Write-Host "Step 1: Starting database services..." -ForegroundColor Cyan
docker compose up -d postgres redis

# Wait for database services to be ready
Write-Host "Waiting for database services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Step 2: Start backend service
Write-Host "Step 2: Starting backend service..." -ForegroundColor Cyan
docker compose up -d backend

# Wait for backend service to be ready
Write-Host "Waiting for backend service to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service status
Write-Host ""
Write-Host "Checking service status..." -ForegroundColor Yellow
docker compose ps

Write-Host ""
Write-Host "🎉 Environment started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Database: localhost:5432" -ForegroundColor White
Write-Host "  Redis: localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Wait for all services to be healthy" -ForegroundColor White
Write-Host "  2. Run database migrations: docker exec bridge_line_backend alembic upgrade head" -ForegroundColor White
Write-Host "  3. Check logs: docker compose logs -f" -ForegroundColor White 