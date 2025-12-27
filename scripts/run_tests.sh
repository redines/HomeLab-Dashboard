#!/bin/bash

# HomeLab Dashboard Test Runner Script
# This script runs all tests (backend, frontend, integration) with proper configuration

set -e  # Exit on error

# Change to project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check and install dependencies
check_and_install_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"
    
    NEEDS_INSTALL=false
    
    # Check Python dependencies
    if ! command_exists pytest; then
        echo -e "${YELLOW}⚠ pytest not found${NC}"
        NEEDS_INSTALL=true
    fi
    
    # Check if npm dependencies are installed
    if [ ! -d "node_modules" ] || ! command_exists jest; then
        echo -e "${YELLOW}⚠ Frontend dependencies not found${NC}"
        NEEDS_INSTALL=true
    fi
    
    if [ "$NEEDS_INSTALL" = true ]; then
        echo ""
        echo -e "${YELLOW}Some dependencies are missing. Would you like to install them now? (y/n)${NC}"
        read -r response
        
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo ""
            echo -e "${BLUE}Installing dependencies...${NC}"
            
            # Install Python dependencies
            if ! command_exists pytest; then
                echo -e "${BLUE}Installing Python test dependencies...${NC}"
                pip install -r requirements.txt
            fi
            
            # Install npm dependencies
            if [ ! -d "node_modules" ] || ! command_exists jest; then
                echo -e "${BLUE}Installing frontend test dependencies...${NC}"
                npm install
            fi
            
            echo -e "${GREEN}✓ Dependencies installed successfully!${NC}"
            echo ""
        else
            echo -e "${RED}Cannot run tests without dependencies.${NC}"
            echo "Please run:"
            echo "  pip install -r requirements.txt"
            echo "  npm install"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ All dependencies found${NC}"
    fi
    echo ""
}

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}HomeLab Dashboard Test Suite${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check and install dependencies if needed
check_and_install_dependencies

# Parse command line arguments
TEST_TYPE="${1:-all}"  # all, backend, frontend, integration, unit
COVERAGE="${2:-true}"  # true or false

# Function to run backend tests
run_backend_tests() {
    echo -e "${BLUE}Running Backend Tests (pytest)...${NC}"
    
    if [ "$COVERAGE" = "true" ]; then
        pytest tests/ \
            --cov=dashboard \
            --cov-report=term-missing \
            --cov-report=html:coverage/backend \
            --cov-report=xml:coverage/backend/coverage.xml \
            -v \
            --tb=short \
            "$@"
    else
        pytest tests/ -v --tb=short "$@"
    fi
    
    BACKEND_EXIT_CODE=$?
    
    if [ $BACKEND_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✓ Backend tests passed!${NC}"
    else
        echo -e "${RED}✗ Backend tests failed!${NC}"
        return $BACKEND_EXIT_CODE
    fi
}

# Function to run frontend tests
run_frontend_tests() {
    echo -e "${BLUE}Running Frontend Tests (Jest)...${NC}"
    
    if [ "$COVERAGE" = "true" ]; then
        npm test -- --coverage --verbose
    else
        npm test -- --verbose
    fi
    
    FRONTEND_EXIT_CODE=$?
    
    if [ $FRONTEND_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✓ Frontend tests passed!${NC}"
    else
        echo -e "${RED}✗ Frontend tests failed!${NC}"
        return $FRONTEND_EXIT_CODE
    fi
}

# Main test execution based on type
case "$TEST_TYPE" in
    backend)
        echo -e "${YELLOW}Running Backend Tests Only${NC}"
        run_backend_tests
        ;;
    
    frontend)
        echo -e "${YELLOW}Running Frontend Tests Only${NC}"
        run_frontend_tests
        ;;
    
    unit)
        echo -e "${YELLOW}Running Unit Tests Only${NC}"
        run_backend_tests -m "unit"
        run_frontend_tests
        ;;
    
    integration)
        echo -e "${YELLOW}Running Integration Tests Only${NC}"
        run_backend_tests -m "integration"
        ;;
    
    all)
        echo -e "${YELLOW}Running All Tests${NC}"
        echo ""
        
        # Run backend tests
        run_backend_tests
        BACKEND_RESULT=$?
        echo ""
        
        # Run frontend tests
        run_frontend_tests
        FRONTEND_RESULT=$?
        echo ""
        
        # Summary
        echo -e "${BLUE}======================================${NC}"
        echo -e "${BLUE}Test Summary${NC}"
        echo -e "${BLUE}======================================${NC}"
        
        if [ $BACKEND_RESULT -eq 0 ] && [ $FRONTEND_RESULT -eq 0 ]; then
            echo -e "${GREEN}✓ All tests passed!${NC}"
            
            if [ "$COVERAGE" = "true" ]; then
                echo ""
                echo -e "${BLUE}Coverage reports generated:${NC}"
                echo -e "  Backend:  coverage/backend/index.html"
                echo -e "  Frontend: coverage/frontend/lcov-report/index.html"
            fi
            
            exit 0
        else
            echo -e "${RED}✗ Some tests failed!${NC}"
            [ $BACKEND_RESULT -ne 0 ] && echo -e "${RED}  - Backend tests failed${NC}"
            [ $FRONTEND_RESULT -ne 0 ] && echo -e "${RED}  - Frontend tests failed${NC}"
            exit 1
        fi
        ;;
    
    *)
        echo -e "${RED}Invalid test type: $TEST_TYPE${NC}"
        echo "Usage: ./run_tests.sh [all|backend|frontend|unit|integration] [coverage:true|false]"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                    # Run all tests with coverage"
        echo "  ./run_tests.sh backend            # Run only backend tests"
        echo "  ./run_tests.sh frontend false     # Run frontend tests without coverage"
        echo "  ./run_tests.sh unit               # Run only unit tests"
        echo "  ./run_tests.sh integration        # Run only integration tests"
        exit 1
        ;;
esac
