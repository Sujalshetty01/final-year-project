#!/bin/bash
# Script to rebuild and run the React frontend Docker container
# Requirements: Docker must be installed and running

set -e

# Function to check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Stop and remove any existing container named "frontend-container"
echo "Stopping and removing existing container (if any)..."
docker stop frontend-container 2>/dev/null || true
docker rm frontend-container 2>/dev/null || true

# Remove the old Docker image (optional)
echo "Removing old Docker image (if any)..."
docker rmi frontend-image 2>/dev/null || true

# Build a new Docker image
echo "Building new Docker image..."
if ! docker build -t frontend-image .; then
    echo "Docker build failed. Check the Dockerfile and try again."
    exit 1
fi

# Run a new container
echo "Running new container..."
if ! docker run -d --name frontend-container -p 8090:8090 frontend-image; then
    echo "Failed to start the frontend container."
    exit 1
fi

# Wait for the container to initialize
sleep 5

# Health check
if curl -s http://localhost:8090 > /dev/null; then
    echo "Frontend is running at http://localhost:8090"
else
    echo "Frontend may not have started correctly. Check the container logs."
fi
