@echo off
REM Script to diagnose and fix Dockerized React frontend issues on http://localhost:8091
REM Cross-platform: Windows

REM 1. Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker first.
    exit /b 1
)

echo [INFO] Docker is installed.

REM 2. Stop and remove existing container
echo [INFO] Stopping and removing any existing 'frontend-container'...
docker stop frontend-container >nul 2>nul

docker rm frontend-container >nul 2>nul

REM 3. Remove old image (optional)
echo [INFO] Removing old Docker image 'frontend-image' (if exists)...
docker rmi frontend-image >nul 2>nul

REM 4. Build new Docker image
echo [INFO] Building new Docker image from Dockerfile...
docker build -t frontend-image .
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker build failed. Check the Dockerfile and try again.
    exit /b 1
)

REM 5. Run new container (map 8091:8091)
echo [INFO] Running new container on port 8091...
docker run -d -p 8091:8091 --name frontend-container frontend-image
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to start the frontend container.
    exit /b 1
)

REM 6. Verify container status
echo [INFO] Checking container status...
docker ps | findstr frontend-container >nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Container failed to start. Logs:
    docker logs frontend-container
    exit /b 1
)

echo [INFO] Container is running. Waiting for app to start...
ping -n 9 127.0.0.1 >nul

REM 7. Health check
curl -s http://localhost:8091 >nul 2>nul
if %ERRORLEVEL%==0 (
    echo [SUCCESS] Frontend is running successfully at http://localhost:8091
) else (
    echo [ERROR] Frontend is not accessible. Container logs:
    docker logs frontend-container
    exit /b 1
)
