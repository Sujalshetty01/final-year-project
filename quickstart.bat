@echo off
REM Quick Start Script for Windows
REM Malware Classification System

setlocal enabledelayedexpansion

echo ==================================
echo Malware Classification System
echo Quick Start Script (Windows)
echo ==================================
echo.

REM Check if .env exists
if not exist .env (
    echo Copying .env.example to .env
    copy .env.example .env
    echo Environment file created
) else (
    echo Environment file exists
)
echo.

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker found
) else (
    echo [WARNING] Docker not found
)

docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] docker-compose found
) else (
    echo [WARNING] docker-compose not found
)

echo.
echo Starting services with docker-compose...
docker-compose up -d

echo.
echo Waiting for services to start...
timeout /t 5 /nobreak

echo.
echo [OK] Services started!
echo.
echo Access the application at:
echo - Frontend: http://localhost:8080
echo - API: http://localhost:8000
echo - API Documentation: http://localhost:8000/docs
echo.
echo To check service status: docker-compose ps
echo To view logs: docker-compose logs -f
echo To stop services: docker-compose down
echo.
pause
