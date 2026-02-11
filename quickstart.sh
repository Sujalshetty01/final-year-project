#!/bin/bash
# Quick Start Script for Malware Classification System
# Supports both Docker and local development setups

set -e

echo "=================================="
echo "Malware Classification System"
echo "Quick Start Script"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    if ! docker --version &> /dev/null; then
        echo -e "${YELLOW}Warning: Docker not found${NC}"
    else
        echo -e "${GREEN}✓ Docker found${NC}"
    fi
    
    if ! docker-compose --version &> /dev/null; then
        echo -e "${YELLOW}Warning: docker-compose not found${NC}"
    else
        echo -e "${GREEN}✓ docker-compose found${NC}"
    fi
    
    if ! python3 --version &> /dev/null; then
        echo -e "${YELLOW}Warning: Python not found${NC}"
    else
        echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"
    fi
    echo ""
}

# Setup environment
setup_environment() {
    echo -e "${BLUE}Setting up environment...${NC}"
    
    if [ ! -f .env ]; then
        echo "Copying .env.example to .env"
        cp .env.example .env
        echo -e "${GREEN}✓ Environment file created${NC}"
    else
        echo -e "${GREEN}✓ Environment file exists${NC}"
    fi
    echo ""
}

# Docker deployment
deploy_docker() {
    echo -e "${BLUE}Deploying with Docker Compose...${NC}"
    
    echo "Building images..."
    docker-compose build
    
    echo "Starting services..."
    docker-compose up -d
    
    echo "Waiting for services to be ready..."
    sleep 5
    
    echo ""
    echo -e "${GREEN}Services started${NC}"
}

# Local deployment
deploy_local() {
    echo -e "${BLUE}Setting up local development environment...${NC}"
    
    # Backend setup
    echo "Setting up backend..."
    python3 -m venv venv
    source venv/bin/activate || . venv/Scripts/activate
    pip install -r backend/requirements.txt
    pip install -r backend/requirements-ml.txt
    
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
    
    # Frontend setup
    echo "Frontend is ready (static files in frontend/public)"
    echo -e "${GREEN}✓ Frontend ready${NC}"
    
    echo ""
    echo "To start services locally, run:"
    echo "  # Backend:"
    echo "  source venv/bin/activate"
    echo "  cd backend && python -m uvicorn app.main:app --reload"
    echo ""
    echo "  # Frontend (in another terminal):"
    echo "  cd frontend/public && python -m http.server 8080"
    echo ""
}

# Verify deployment
verify_deployment() {
    echo -e "${BLUE}Verifying deployment...${NC}"
    
    echo "Waiting for API to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/v1/health &> /dev/null; then
            echo -e "${GREEN}✓ API is ready${NC}"
            break
        fi
        echo "Waiting... ($i/30)"
        sleep 1
    done
    
    if curl -s http://localhost:8080 &> /dev/null; then
        echo -e "${GREEN}✓ Frontend is ready${NC}"
    else
        echo -e "${YELLOW}Warning: Could not reach frontend${NC}"
    fi
    echo ""
}

# Show summary
show_summary() {
    echo -e "${GREEN}=================================="
    echo "Setup Complete!"
    echo "==================================${NC}"
    echo ""
    echo "Access the application at:"
    echo -e "  ${BLUE}Frontend:${NC} http://localhost:8080"
    echo -e "  ${BLUE}API:${NC} http://localhost:8000"
    echo -e "  ${BLUE}API Docs:${NC} http://localhost:8000/docs"
    echo ""
    echo "To stop services:"
    echo -e "  ${YELLOW}docker-compose down${NC}"
    echo ""
    echo "For more information, see README.md"
    echo ""
}

# Main script
main() {
    check_prerequisites
    setup_environment
    
    # Ask user for deployment method
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        echo "Available deployment options:"
        echo "1) Docker (recommended)"
        echo "2) Local development"
        echo ""
        read -p "Choose deployment method (1 or 2): " choice
        
        case $choice in
            1) deploy_docker ;;
            2) deploy_local ;;
            *) 
                echo "Using Docker (default)"
                deploy_docker
                ;;
        esac
    else
        echo "Docker not found. Setting up local development environment..."
        deploy_local
    fi
    
    # Try to verify (may not work if local setup)
    if [ "$choice" != "2" ]; then
        verify_deployment
    fi
    
    show_summary
}

# Run main function
main
