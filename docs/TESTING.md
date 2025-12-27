# Testing Guide

This document provides comprehensive information about the testing setup for the HomeLab Dashboard project.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)
- [Coverage Reports](#coverage-reports)

## Overview

The HomeLab Dashboard uses a comprehensive testing strategy that includes:

- **Backend Tests**: Django/Python tests using pytest
- **Frontend Tests**: JavaScript tests using Jest
- **Integration Tests**: End-to-end workflow tests
- **Unit Tests**: Isolated component tests

## Test Structure

```
HomeLab-Dashboard/
├── tests/                      # Backend test directory
│   ├── __init__.py
│   ├── test_models.py         # Model tests
│   ├── test_utilities.py      # Utility module tests
│   ├── test_views.py          # View and API tests
│   ├── test_integration.py    # Integration tests
│   └── frontend/              # Frontend test directory
│       ├── setup.js           # Jest setup
│       └── dashboard.test.js  # Dashboard JS tests
├── conftest.py                # Pytest fixtures and configuration
├── pytest.ini                 # Pytest configuration
├── jest.config.json           # Jest configuration
└── run_tests.sh              # Test runner script
```

## Running Tests

### Quick Start

Run all tests:
```bash
./scripts/run_tests.sh
```

### Backend Tests Only

```bash
./scripts/run_tests.sh backend
```

Or directly with pytest:
```bash
pytest tests/ -v
```

### Frontend Tests Only

```bash
./scripts/run_tests.sh frontend
```

Or directly with npm:
```bash
npm test
```

### Unit Tests Only

```bash
./scripts/run_tests.sh unit
```

This runs:
- Backend unit tests (models, utilities)
- Frontend unit tests (JavaScript functions)

### Integration Tests Only

```bash
./scripts/run_tests.sh integration
```

### Running Specific Test Files

Backend:
```bash
pytest tests/test_models.py -v
pytest tests/test_views.py -v
```

Frontend:
```bash
npm test -- tests/frontend/dashboard.test.js
```

### Running Tests by Markers

Backend tests are organized with pytest markers:

```bash
# Unit tests
pytest -m unit

# Integration tests
pytest -m integration

# Model tests
pytest -m models

# View tests
pytest -m views

# API tests
pytest -m api

# Slow tests
pytest -m slow
```

### Running Tests Without Coverage

```bash
./scripts/run_tests.sh all false
```

### Watch Mode (Frontend)

```bash
npm run test:watch
```

## Writing Tests

### Backend Tests (pytest)

#### Creating a Test File

```python
import pytest
from django.test import Client
from dashboard.models import Service

@pytest.mark.django_db
@pytest.mark.unit
class TestServiceModel:
    def test_create_service(self):
        service = Service.objects.create(
            name='Test Service',
            url='https://test.local'
        )
        assert service.name == 'Test Service'
```

#### Using Fixtures

Fixtures are defined in `conftest.py`:

```python
def test_with_sample_service(sample_service):
    """Test using the sample_service fixture."""
    assert sample_service.name == 'Test Service'
    assert sample_service.status == 'up'

def test_with_api_client(api_client):
    """Test using the Django test client."""
    response = api_client.get('/')
    assert response.status_code == 200
```

#### Available Fixtures

- `api_client`: Django test client
- `sample_service`: Single test service
- `sample_services`: Multiple test services
- `manual_service`: Manually added service
- `service_with_api`: Service with API integration
- `health_check`: Health check record
- `grafana_panel`: Grafana panel
- `mock_requests_success`: Mock successful HTTP requests
- `mock_requests_failure`: Mock failed HTTP requests
- `mock_requests_timeout`: Mock timeout errors

#### Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit           # Unit test
@pytest.mark.integration    # Integration test
@pytest.mark.models         # Model test
@pytest.mark.views          # View test
@pytest.mark.api            # API test
@pytest.mark.slow           # Slow test (>1 second)
```

### Frontend Tests (Jest)

#### Creating a Test File

```javascript
describe('Dashboard Functions', () => {
  test('getCookie retrieves CSRF token', () => {
    document.cookie = 'csrftoken=test123';
    
    const getCookie = (name) => {
      // Implementation
    };
    
    expect(getCookie('csrftoken')).toBe('test123');
  });
});
```

#### Mocking

```javascript
test('refreshServices makes API call', async () => {
  global.fetch = jest.fn().mockResolvedValue({
    json: () => Promise.resolve({ success: true })
  });
  
  await refreshServices();
  
  expect(fetch).toHaveBeenCalledWith(
    '/api/services/refresh/',
    expect.any(Object)
  );
});
```

#### DOM Testing

```javascript
beforeEach(() => {
  document.body.innerHTML = `
    <div id="loading-overlay"></div>
    <button id="refresh-btn"></button>
  `;
});

test('shows loading overlay', () => {
  const overlay = document.getElementById('loading-overlay');
  overlay.style.display = 'flex';
  
  expect(overlay.style.display).toBe('flex');
});
```

## CI/CD Integration

### GitHub Actions

The project includes a GitHub Actions workflow (`.github/workflows/tests.yml`) that automatically runs tests on:

- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

The workflow includes:

1. **Backend Tests**: Runs on Python 3.10, 3.11, and 3.12
2. **Frontend Tests**: Runs on Node 18.x and 20.x
3. **Integration Tests**: Full workflow tests
4. **Linting**: Code quality checks (flake8, black, isort)
5. **Coverage Upload**: Uploads coverage to Codecov

### Running Tests in CI

Tests run automatically but can be manually triggered:

```bash
# In GitHub Actions UI: 
# Actions → Test Suite → Run workflow
```

### Environment Variables for CI

Required environment variables:

```bash
DJANGO_SETTINGS_MODULE=homelab_dashboard.settings
SECRET_KEY=<your-secret-key>
FIELD_ENCRYPTION_KEY=<your-encryption-key>
```

## Coverage Reports

### Viewing Coverage

After running tests with coverage, view the reports:

#### Backend Coverage

```bash
# Terminal summary (shown automatically)
pytest tests/ --cov=dashboard --cov-report=term-missing

# HTML report
open coverage/backend/index.html
```

#### Frontend Coverage

```bash
# Terminal summary (shown automatically)
npm test -- --coverage

# HTML report
open coverage/frontend/lcov-report/index.html
```

### Coverage Targets

Aim for:
- **Overall**: 80%+ coverage
- **Models**: 90%+ coverage
- **Views**: 80%+ coverage
- **Utilities**: 85%+ coverage
- **Frontend**: 75%+ coverage

### Excluding Files from Coverage

Edit `pytest.ini` or `jest.config.json` to exclude files:

```ini
# pytest.ini
[pytest]
addopts = 
    --cov-omit=*/migrations/*,*/tests/*,*/venv/*
```

```json
// jest.config.json
{
  "collectCoverageFrom": [
    "static/js/**/*.js",
    "!static/js/**/*.min.js"
  ]
}
```

## Test Best Practices

### Backend Tests

1. **Use fixtures**: Reuse test data with fixtures
2. **Mark tests**: Use pytest markers for organization
3. **Mock external calls**: Mock API calls, file I/O
4. **Test edge cases**: Include error conditions
5. **Keep tests isolated**: Each test should be independent
6. **Use descriptive names**: Test names should describe behavior

### Frontend Tests

1. **Mock DOM**: Set up DOM elements in beforeEach
2. **Mock fetch**: Mock all network calls
3. **Test user interactions**: Simulate clicks, input
4. **Test edge cases**: Empty states, errors
5. **Clean up**: Clear mocks in afterEach
6. **Avoid implementation details**: Test behavior, not internals

### Integration Tests

1. **Test complete workflows**: End-to-end user scenarios
2. **Use realistic data**: Test with production-like data
3. **Test error paths**: Include failure scenarios
4. **Keep them focused**: One workflow per test
5. **Mark as integration**: Use `@pytest.mark.integration`

## Troubleshooting

### Common Issues

#### Database Errors

```bash
# Reset test database
pytest --create-db
```

#### Import Errors

```bash
# Ensure in correct directory
cd /path/to/HomeLab-Dashboard

# Check PYTHONPATH
export PYTHONPATH=$(pwd)
```

#### Frontend Test Failures

```bash
# Clear Jest cache
npm test -- --clearCache

# Reinstall dependencies
rm -rf node_modules
npm install
```

#### Coverage Not Showing

```bash
# Reinstall coverage tools
pip install --upgrade pytest-cov coverage

# For frontend
npm install --save-dev jest
```

### Getting Help

- Review test output carefully
- Check fixture setup in `conftest.py`
- Verify environment variables are set
- Run tests in verbose mode: `pytest -vv` or `npm test -- --verbose`

## Continuous Improvement

### Adding New Tests

When adding new features:

1. Write tests first (TDD approach)
2. Add unit tests for new models/functions
3. Add view tests for new endpoints
4. Add integration tests for workflows
5. Update this documentation if needed

### Maintaining Tests

- Review and update tests when code changes
- Remove obsolete tests
- Refactor duplicate test code into fixtures
- Keep test data realistic but minimal
- Monitor coverage trends

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Jest Documentation](https://jestjs.io/)
- [Testing Best Practices](https://testingjavascript.com/)
