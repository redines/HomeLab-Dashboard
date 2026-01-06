# HomeLab Dashboard Test Runner Script for Windows
# This script runs all tests (backend, frontend, integration) with proper configuration

# Change to project root directory (parent of scripts/)
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$SCRIPT_DIR\.."

# Function to check if command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to check and install dependencies
function Test-Dependencies {
    Write-Host "Checking dependencies..." -ForegroundColor Blue
    
    $NEEDS_INSTALL = $false
    
    # Check Python dependencies
    try {
        python -c "import pytest" 2>$null
    } catch {
        Write-Host "⚠ pytest not found" -ForegroundColor Yellow
        $NEEDS_INSTALL = $true
    }
    
    # Check if npm dependencies are installed
    if (-not (Test-Path "node_modules") -or -not (Test-Command "jest")) {
        Write-Host "⚠ Frontend dependencies not found" -ForegroundColor Yellow
        $NEEDS_INSTALL = $true
    }
    
    if ($NEEDS_INSTALL) {
        Write-Host ""
        $response = Read-Host "Some dependencies are missing. Would you like to install them now? (y/n)"
        
        if ($response -match "^[Yy]$") {
            Write-Host ""
            Write-Host "Installing dependencies..." -ForegroundColor Blue
            
            # Install Python dependencies
            Write-Host "Installing Python test dependencies..." -ForegroundColor Blue
            pip install -r requirements.txt
            
            # Install npm dependencies
            Write-Host "Installing frontend test dependencies..." -ForegroundColor Blue
            npm install
            
            Write-Host "✓ Dependencies installed successfully!" -ForegroundColor Green
            Write-Host ""
        } else {
            Write-Host "Cannot run tests without dependencies." -ForegroundColor Red
            Write-Host "Please run:"
            Write-Host "  pip install -r requirements.txt"
            Write-Host "  npm install"
            exit 1
        }
    } else {
        Write-Host "✓ All dependencies found" -ForegroundColor Green
    }
    Write-Host ""
}

Write-Host "======================================" -ForegroundColor Blue
Write-Host "HomeLab Dashboard Test Suite" -ForegroundColor Blue
Write-Host "======================================" -ForegroundColor Blue
Write-Host ""

# Check and install dependencies if needed
Test-Dependencies

# Parse command line arguments
$TEST_TYPE = if ($args.Count -gt 0) { $args[0] } else { "all" }
$COVERAGE = if ($args.Count -gt 1) { $args[1] } else { "true" }

# Function to run backend tests
function Invoke-BackendTests {
    Write-Host "Running Backend Tests (pytest)..." -ForegroundColor Blue
    
    if ($COVERAGE -eq "true") {
        python -m pytest tests/ `
            --cov=dashboard `
            --cov-report=term-missing `
            --cov-report=html:coverage/backend `
            --cov-report=xml:coverage/backend/coverage.xml `
            -v `
            --tb=short `
            --color=yes
    } else {
        python -m pytest tests/ -v --tb=short --color=yes
    }
    
    $BACKEND_EXIT = $LASTEXITCODE
    Write-Host ""
    return $BACKEND_EXIT
}

# Function to run frontend tests
function Invoke-FrontendTests {
    Write-Host "Running Frontend Tests (Jest)..." -ForegroundColor Blue
    
    if ($COVERAGE -eq "true") {
        npm test -- --coverage --colors
    } else {
        npm test -- --colors
    }
    
    $FRONTEND_EXIT = $LASTEXITCODE
    Write-Host ""
    return $FRONTEND_EXIT
}

# Function to run integration tests
function Invoke-IntegrationTests {
    Write-Host "Running Integration Tests..." -ForegroundColor Blue
    
    python -m pytest tests/ -m "integration" -v --tb=short --color=yes
    
    $INTEGRATION_EXIT = $LASTEXITCODE
    Write-Host ""
    return $INTEGRATION_EXIT
}

# Function to run unit tests only
function Invoke-UnitTests {
    Write-Host "Running Unit Tests..." -ForegroundColor Blue
    
    if ($COVERAGE -eq "true") {
        python -m pytest tests/ -m "not integration" `
            --cov=dashboard `
            --cov-report=term-missing `
            --cov-report=html:coverage/unit `
            -v `
            --tb=short `
            --color=yes
    } else {
        python -m pytest tests/ -m "not integration" -v --tb=short --color=yes
    }
    
    $UNIT_EXIT = $LASTEXITCODE
    Write-Host ""
    return $UNIT_EXIT
}

# Main test execution
$BACKEND_EXIT = 0
$FRONTEND_EXIT = 0
$INTEGRATION_EXIT = 0
$UNIT_EXIT = 0

switch ($TEST_TYPE.ToLower()) {
    "backend" {
        Write-Host "Test Mode: Backend Only" -ForegroundColor Cyan
        Write-Host ""
        $BACKEND_EXIT = Invoke-BackendTests
    }
    "frontend" {
        Write-Host "Test Mode: Frontend Only" -ForegroundColor Cyan
        Write-Host ""
        $FRONTEND_EXIT = Invoke-FrontendTests
    }
    "integration" {
        Write-Host "Test Mode: Integration Only" -ForegroundColor Cyan
        Write-Host ""
        $INTEGRATION_EXIT = Invoke-IntegrationTests
    }
    "unit" {
        Write-Host "Test Mode: Unit Tests Only" -ForegroundColor Cyan
        Write-Host ""
        $UNIT_EXIT = Invoke-UnitTests
    }
    "all" {
        Write-Host "Test Mode: All Tests" -ForegroundColor Cyan
        Write-Host ""
        
        $BACKEND_EXIT = Invoke-BackendTests
        $FRONTEND_EXIT = Invoke-FrontendTests
        $INTEGRATION_EXIT = Invoke-IntegrationTests
    }
    default {
        Write-Host "Unknown test type: $TEST_TYPE" -ForegroundColor Red
        Write-Host "Valid options: all, backend, frontend, integration, unit" -ForegroundColor Yellow
        exit 1
    }
}

# Summary
Write-Host "======================================" -ForegroundColor Blue
Write-Host "Test Results Summary" -ForegroundColor Blue
Write-Host "======================================" -ForegroundColor Blue

$ALL_PASSED = $true

if ($TEST_TYPE -eq "all" -or $TEST_TYPE -eq "backend") {
    if ($BACKEND_EXIT -eq 0) {
        Write-Host "✓ Backend Tests: PASSED" -ForegroundColor Green
    } else {
        Write-Host "✗ Backend Tests: FAILED" -ForegroundColor Red
        $ALL_PASSED = $false
    }
}

if ($TEST_TYPE -eq "all" -or $TEST_TYPE -eq "frontend") {
    if ($FRONTEND_EXIT -eq 0) {
        Write-Host "✓ Frontend Tests: PASSED" -ForegroundColor Green
    } else {
        Write-Host "✗ Frontend Tests: FAILED" -ForegroundColor Red
        $ALL_PASSED = $false
    }
}

if ($TEST_TYPE -eq "all" -or $TEST_TYPE -eq "integration") {
    if ($INTEGRATION_EXIT -eq 0) {
        Write-Host "✓ Integration Tests: PASSED" -ForegroundColor Green
    } else {
        Write-Host "✗ Integration Tests: FAILED" -ForegroundColor Red
        $ALL_PASSED = $false
    }
}

if ($TEST_TYPE -eq "unit") {
    if ($UNIT_EXIT -eq 0) {
        Write-Host "✓ Unit Tests: PASSED" -ForegroundColor Green
    } else {
        Write-Host "✗ Unit Tests: FAILED" -ForegroundColor Red
        $ALL_PASSED = $false
    }
}

Write-Host "======================================" -ForegroundColor Blue
Write-Host ""

if ($COVERAGE -eq "true") {
    Write-Host "📊 Coverage reports available at:" -ForegroundColor Cyan
    if (Test-Path "coverage/backend") {
        Write-Host "   Backend: coverage/backend/index.html" -ForegroundColor Gray
    }
    if (Test-Path "coverage") {
        Write-Host "   Frontend: coverage/lcov-report/index.html" -ForegroundColor Gray
    }
    Write-Host ""
}

# Exit with appropriate code
if ($ALL_PASSED) {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Some tests failed!" -ForegroundColor Red
    exit 1
}
