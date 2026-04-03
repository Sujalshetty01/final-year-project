#!/bin/bash
# Script to diagnose and fix Dockerized React frontend issues on http://localhost:8091
# Cross-platform: Linux/Mac

set -e

# 1. Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed. Please install Docker first."
    exit 1
fi

echo "[INFO] Docker is installed."

# 2. Stop and remove existing container
echo "[INFO] Stopping and removing any existing 'frontend-container'..."
docker stop frontend-container 2>/dev/null || true
docker rm frontend-container 2>/dev/null || true

# 3. Remove old image (optional)
echo "[INFO] Removing old Docker image 'frontend-image' (if exists)..."
docker rmi frontend-image 2>/dev/null || true

# 4. Build new Docker image
echo "[INFO] Building new Docker image from Dockerfile..."
if ! docker build -t frontend-image .; then
    echo "[ERROR] Docker build failed. Check the Dockerfile and try again."
    exit 1
fi

# 5. Run new container (map 8091:8091)
echo "[INFO] Running new container on port 8091..."
if ! docker run -d -p 8091:8091 --name frontend-container frontend-image; then
    echo "[ERROR] Failed to start the frontend container."
    exit 1
fi

# 6. Verify container status
echo "[INFO] Checking container status..."
if ! docker ps | grep frontend-container > /dev/null; then
    echo "[ERROR] Container failed to start. Logs:"
    docker logs frontend-container || true
    exit 1
fi

echo "[INFO] Container is running. Waiting for app to start..."
sleep 8

# 7. Health check
if curl -s http://localhost:8091 > /dev/null; then
    echo "[SUCCESS] Frontend is running successfully at http://localhost:8091"
else
    echo "[ERROR] Frontend is not accessible. Container logs:"
    docker logs frontend-container || true
    exit 1
fi
