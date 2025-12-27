# Quick Test Reference

## Installation

```bash
# Install backend test dependencies
pip install -r requirements.txt

# Install frontend test dependencies
npm install
```

## Running Tests

| Command | Description |
|---------|-------------|
| `./scripts/run_tests.sh` | Run all tests with coverage |
| `./scripts/run_tests.sh backend` | Run only backend tests |
| `./scripts/run_tests.sh frontend` | Run only frontend tests |
| `./scripts/run_tests.sh unit` | Run only unit tests |
| `./scripts/run_tests.sh integration` | Run only integration tests |
| `./scripts/run_tests.sh all false` | Run all tests without coverage |

## Backend (pytest)

```bash
# Run all backend tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run specific test class
pytest tests/test_models.py::TestServiceModel

# Run specific test method
pytest tests/test_models.py::TestServiceModel::test_create_service

# Run tests by marker
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m models        # Model tests only
pytest -m views         # View tests only
pytest -m api           # API tests only

# Run with coverage
pytest --cov=dashboard --cov-report=html

# Run in parallel (faster)
pytest -n auto
```

## Frontend (Jest)

```bash
# Run all frontend tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm test -- tests/frontend/dashboard.test.js

# Run tests matching pattern
npm test -- --testNamePattern="getCookie"

# Update snapshots
npm test -- -u
```

## Common Patterns

### Debug Failed Test

```bash
# Backend: Show full traceback
pytest -vv --tb=long

# Frontend: Run single test in watch mode
npm test -- --watch tests/frontend/dashboard.test.js
```

### Check Coverage

```bash
# Backend
pytest --cov=dashboard --cov-report=term-missing

# Frontend
npm test -- --coverage --coverageReporters=text
```

### Run Fast Tests Only

```bash
# Skip slow tests
pytest -m "not slow"
```

## Test Files

| File | Purpose |
|------|---------|
| `tests/test_models.py` | Model unit tests |
| `tests/test_views.py` | View and API endpoint tests |
| `tests/test_utilities.py` | Utility module tests |
| `tests/test_integration.py` | Integration/workflow tests |
| `tests/frontend/dashboard.test.js` | Frontend JavaScript tests |

## Fixtures

Available pytest fixtures in `conftest.py`:
- `api_client` - Django test client
- `sample_service` - Single test service
- `sample_services` - Multiple test services
- `service_with_api` - Service with API config
- `grafana_panel` - Test Grafana panel
- `mock_requests_success` - Mock successful HTTP
- `mock_requests_failure` - Mock failed HTTP

## Test Markers

```python
@pytest.mark.django_db    # Enables database access
@pytest.mark.unit         # Unit test
@pytest.mark.integration  # Integration test
@pytest.mark.models       # Model test
@pytest.mark.views        # View test
@pytest.mark.api          # API test
@pytest.mark.slow         # Slow test (>1s)
```

## CI/CD

Tests run automatically on:
- Push to `main` or `develop`
- Pull requests
- Manual workflow trigger

View results at: `Actions` tab in GitHub

## Troubleshooting

```bash
# Clear pytest cache
pytest --cache-clear

# Clear Jest cache
npm test -- --clearCache

# Reinstall dependencies
pip install -r requirements.txt
npm install

# Check test discovery
pytest --collect-only

# Run with debugging
pytest --pdb  # Drop into debugger on failure
```

## Coverage Reports

After running tests with coverage:

- Backend: `coverage/backend/index.html`
- Frontend: `coverage/frontend/lcov-report/index.html`

Open in browser:
```bash
open coverage/backend/index.html
open coverage/frontend/lcov-report/index.html
```
