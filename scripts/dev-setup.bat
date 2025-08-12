@echo off
REM Bridge Line Development Setup Script for Windows
REM Batch file for setting up the development environment

echo 🚀 Bridge Line Development Environment Setup for Windows
echo.

REM Check if Docker is running
echo Checking Docker status...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo ✅ Docker is running

REM Check if Docker Compose is available
echo Checking Docker Compose...
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not available. Please update Docker Desktop.
    pause
    exit /b 1
)
echo ✅ Docker Compose is available

REM Start the environment
echo.
echo Starting Bridge Line environment...

REM Step 1: Start database services
echo Step 1: Starting database services...
docker compose up -d postgres redis

REM Wait for database services to be ready
echo Waiting for database services to be ready...
timeout /t 20 /nobreak >nul

REM Step 2: Start backend service
echo Step 2: Starting backend service...
docker compose up -d backend

REM Wait for backend service to be ready
echo Waiting for backend service to be ready...
timeout /t 30 /nobreak >nul

REM Check service status
echo.
echo Checking service status...
docker compose ps

echo.
echo 🎉 Environment started successfully!
echo.
echo Access URLs:
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo   Database: localhost:5432
echo   Redis: localhost:6379
echo.
echo Next steps:
echo   1. Wait for all services to be healthy
echo   2. Run database migrations: docker exec bridge_line_backend alembic upgrade head
echo   3. Check logs: docker compose logs -f

pause
