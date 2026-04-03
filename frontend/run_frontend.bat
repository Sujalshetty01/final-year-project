@echo off
REM Script to rebuild and run the React frontend Docker container
REM Requirements: Docker Desktop must be installed and running

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker is not installed. Please install Docker Desktop and try again.
    exit /b 1
)

REM Stop and remove any existing container named "frontend-container"
echo Stopping and removing existing container (if any)...
docker stop frontend-container >nul 2>nul

docker rm frontend-container >nul 2>nul

REM Remove the old Docker image (optional)
echo Removing old Docker image (if any)...
docker rmi frontend-image >nul 2>nul

REM Build a new Docker image
echo Building new Docker image...
docker build -t frontend-image .
if %ERRORLEVEL% neq 0 (
    echo Docker build failed. Check the Dockerfile and try again.
    exit /b 1
)

REM Run a new container
echo Running new container...
docker run -d --name frontend-container -p 8090:8090 frontend-image
if %ERRORLEVEL% neq 0 (
    echo Failed to start the frontend container.
    exit /b 1
)

REM Wait for the container to initialize
ping -n 6 127.0.0.1 >nul

REM Health check
curl -s http://localhost:8090 >nul 2>nul
if %ERRORLEVEL%==0 (
    echo Frontend is running at http://localhost:8090
) else (
    echo Frontend may not have started correctly. Check the container logs.
)
