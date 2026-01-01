# HomeLab Dashboard Tests

This directory contains all automated tests for the HomeLab Dashboard project.

## Test Structure

```
tests/
├── __init__.py                # Tests package init
├── test_models.py            # Django model tests (Service, HealthCheck, GrafanaPanel)
├── test_views.py             # View and API endpoint tests
├── test_utilities.py         # Utility module tests (encryption, API client, Traefik)
├── test_integration.py       # End-to-end integration tests
└── frontend/
    ├── setup.js              # Jest test setup and configuration
    └── dashboard.test.js     # Frontend JavaScript tests
```

## Quick Start

Run all tests:
```bash
./scripts/run_tests.sh
```

Run specific test categories:
```bash
./scripts/run_tests.sh backend      # Backend only
./scripts/run_tests.sh frontend     # Frontend only
./scripts/run_tests.sh unit         # Unit tests only
./scripts/run_tests.sh integration  # Integration tests only
```

## Test Categories

### Backend Tests (pytest)

- **Model Tests** (`test_models.py`)
  - Service model CRUD operations
  - Health check tracking
  - Grafana panel management
  - Encrypted field handling
  - Model validation and constraints

- **View Tests** (`test_views.py`)
  - Dashboard view rendering
  - API endpoints (services, refresh, health checks)
  - Service management (create, update, delete)
  - Grafana panel views
  - API detection endpoints

- **Utility Tests** (`test_utilities.py`)
  - Encryption/decryption functions
  - Generic API client
  - Traefik service synchronization
  - Error handling

- **Integration Tests** (`test_integration.py`)
  - Complete service lifecycle
  - Dashboard refresh workflow
  - Manual service management
  - API detection and configuration
  - Grafana integration
  - Health check history

### Frontend Tests (Jest)

- **Dashboard JavaScript Tests** (`frontend/dashboard.test.js`)
  - Cookie parsing (CSRF token)
  - Service opening in new tab
  - Service refresh functionality
  - Statistics updates
  - Service card updates
  - API communication

## Test Markers

Backend tests use pytest markers for organization:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Multi-component integration tests
- `@pytest.mark.models` - Model-specific tests
- `@pytest.mark.views` - View and endpoint tests
- `@pytest.mark.api` - API integration tests
- `@pytest.mark.slow` - Tests that take >1 second

Run tests by marker:
```bash
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m "not slow"    # Skip slow tests
```

## Fixtures

Common test fixtures are defined in `../conftest.py`:

- `api_client` - Django test client for HTTP requests
- `sample_service` - Single test service instance
- `sample_services` - Multiple test services (5 services)
- `manual_service` - Manually added service
- `service_with_api` - Service with API credentials
- `health_check` - Health check record
- `grafana_panel` - Grafana panel instance
- `mock_requests_success` - Mock successful HTTP responses
- `mock_requests_failure` - Mock failed HTTP connections
- `mock_requests_timeout` - Mock timeout errors

## Writing New Tests

### Backend Test Template

```python
import pytest
from dashboard.models import Service

@pytest.mark.django_db
@pytest.mark.unit
class TestMyFeature:
    def test_feature_works(self, api_client):
        """Test that my feature works correctly."""
        # Arrange
        service = Service.objects.create(name='Test', url='https://test.local')
        
        # Act
        response = api_client.get('/my-endpoint/')
        
        # Assert
        assert response.status_code == 200
```

### Frontend Test Template

```javascript
describe('MyFeature', () => {
  test('feature works correctly', () => {
    // Arrange
    const mockData = { key: 'value' };
    
    // Act
    const result = myFunction(mockData);
    
    // Assert
    expect(result).toBe(expectedValue);
  });
});
```

## Coverage

Test coverage targets:
- Overall: 80%+
- Models: 90%+
- Views: 80%+
- Utilities: 85%+
- Frontend: 75%+

View coverage reports:
```bash
# Backend
open coverage/backend/index.html

# Frontend
open coverage/frontend/lcov-report/index.html
```

## CI/CD

Tests run automatically via GitHub Actions on:
- Push to `main` or `develop`
- Pull requests
- Manual workflow triggers

See `.github/workflows/tests.yml` for configuration.

## Documentation

- [Full Testing Guide](../docs/TESTING.md) - Comprehensive testing documentation
- [Quick Reference](../docs/TEST_QUICK_REFERENCE.md) - Command cheat sheet

## Common Commands

```bash
# Run all tests with coverage
pytest --cov=dashboard --cov-report=html
npm test -- --coverage

# Run specific test file
pytest tests/test_models.py -v
npm test -- tests/frontend/dashboard.test.js

# Run in watch mode (frontend)
npm run test:watch

# Run with debugging
pytest --pdb  # Drops into debugger on failure

# Clear caches
pytest --cache-clear
npm test -- --clearCache
```

## Troubleshooting

If tests fail:

1. Check that all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. Verify environment variables are set (for backend):
   ```bash
   export DJANGO_SETTINGS_MODULE=homelab_dashboard.settings
   ```

3. Clear test caches:
   ```bash
   pytest --cache-clear
   npm test -- --clearCache
   ```

4. Check test discovery:
   ```bash
   pytest --collect-only
   ```

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain coverage above targets
4. Use appropriate markers
5. Document complex test scenarios
