#!/bin/bash
# Script to start Pune School Dashboard services

set -e

echo "=========================================="
echo "Pune School Dashboard - Service Starter"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Navigate to project root (scripts/ is in project root)
cd "$(dirname "$0")/.."

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp config/env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
fi

# Build images
echo ""
echo -e "${YELLOW}Building Docker images...${NC}"
docker compose build

# Start services
echo ""
echo -e "${YELLOW}Starting services...${NC}"
docker compose up -d

# Wait for services to be ready
echo ""
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 10

# Check service status
echo ""
echo -e "${GREEN}Service Status:${NC}"
docker compose ps

# Check health
echo ""
echo -e "${YELLOW}Checking service health...${NC}"

# Backend health
if curl -s http://localhost:8002/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not responding${NC}"
fi

# Frontend health
if curl -s http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${YELLOW}⚠ Frontend may still be starting...${NC}"
fi

# MongoDB
if docker compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MongoDB is running${NC}"
else
    echo -e "${RED}✗ MongoDB is not responding${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Services Started!${NC}"
echo "=========================================="
echo ""
echo "Access the application at:"
echo "  Frontend:    http://localhost"
echo "  Backend API: http://localhost:8002"
echo "  API Docs:    http://localhost:8002/docs"
echo ""
echo "Default Login:"
echo "  Email:    admin@mahaedume.gov.in"
echo "  Password: admin123"
echo ""
echo "To view logs:"
echo "  docker compose logs -f"
echo ""
echo "To stop services:"
echo "  docker compose down"
echo ""

