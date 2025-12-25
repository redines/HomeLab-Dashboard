#!/bin/bash

# HomeLab Dashboard - Testing Script
# This script helps verify that the setup is correct

echo "🧪 HomeLab Dashboard - Setup Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASS=0
FAIL=0

# Check Python version
echo "1️⃣  Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python found: $PYTHON_VERSION"
    ((PASS++))
else
    echo -e "${RED}✗${NC} Python 3 not found"
    ((FAIL++))
fi
echo ""

# Check if Docker is installed
echo "2️⃣  Checking Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} Docker found: $DOCKER_VERSION"
    ((PASS++))
else
    echo -e "${YELLOW}⚠${NC} Docker not found (optional for local development)"
fi
echo ""

# Check if Docker Compose is installed
echo "3️⃣  Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✓${NC} Docker Compose found: $COMPOSE_VERSION"
    ((PASS++))
else
    echo -e "${YELLOW}⚠${NC} Docker Compose not found (optional for local development)"
fi
echo ""

# Check required files
echo "4️⃣  Checking project files..."
FILES=(
    "manage.py"
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
    "homelab_dashboard/settings.py"
    "dashboard/models.py"
    "dashboard/views.py"
    "dashboard/traefik_service.py"
    "templates/dashboard/index.html"
    "static/css/style.css"
    "static/js/dashboard.js"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $file missing"
        ((FAIL++))
    fi
done
echo ""

# Check if .env exists
echo "5️⃣  Checking environment configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    ((PASS++))
else
    echo -e "${YELLOW}⚠${NC} .env file not found"
    echo "   You can copy .env.example to .env and customize it"
fi
echo ""

# Check if virtual environment exists
echo "6️⃣  Checking virtual environment..."
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment found"
    ((PASS++))
else
    echo -e "${YELLOW}⚠${NC} Virtual environment not found"
    echo "   Run './start.sh' or 'python3 -m venv venv' to create it"
fi
echo ""

# Summary
echo "=========================================="
echo "📊 Test Results:"
echo -e "   ${GREEN}Passed: $PASS${NC}"
if [ $FAIL -gt 0 ]; then
    echo -e "   ${RED}Failed: $FAIL${NC}"
fi
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ All critical checks passed!${NC}"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Configure your Traefik API URL in .env or docker-compose.yml"
    echo "   2. Choose your deployment method:"
    echo ""
    echo "      Docker:"
    echo "      $ docker-compose up -d"
    echo "      $ docker-compose exec web python manage.py migrate"
    echo "      $ docker-compose exec web python manage.py createsuperuser"
    echo ""
    echo "      Local:"
    echo "      $ ./start.sh"
    echo ""
    echo "   3. Sync services: python manage.py sync_services"
    echo "   4. Access dashboard: http://localhost:8000"
else
    echo -e "${RED}❌ Some checks failed. Please review the errors above.${NC}"
fi
echo ""
