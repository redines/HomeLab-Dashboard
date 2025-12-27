# Testing Quick Start Guide

Welcome! This guide will help you get started with testing the HomeLab Dashboard in under 5 minutes.

## Step 1: Install Dependencies

```bash
# Install Python test dependencies
pip install -r requirements.txt

# Install JavaScript test dependencies
npm install
```

## Step 2: Run Your First Test

```bash
# Run all tests
./run_tests.sh
```

That's it! You should see output like:

```
======================================
HomeLab Dashboard Test Suite
======================================

Running All Tests

Running Backend Tests (pytest)...
tests/test_models.py::TestServiceModel::test_create_service PASSED
tests/test_models.py::TestServiceModel::test_service_unique_name PASSED
...
✓ Backend tests passed!

Running Frontend Tests (Jest)...
PASS tests/frontend/dashboard.test.js
  ✓ getCookie retrieves CSRF token
  ✓ openService opens URL in new tab
...
✓ Frontend tests passed!

======================================
Test Summary
======================================
✓ All tests passed!
```

## Step 3: Explore Test Options

```bash
# Run only backend tests (faster)
./run_tests.sh backend

# Run only frontend tests
./run_tests.sh frontend

# Run only fast unit tests
./run_tests.sh unit

# Run only integration tests
./run_tests.sh integration

# Run without coverage (faster)
./run_tests.sh all false
```

## Step 4: View Coverage Reports

After running tests with coverage (default), open the reports:

```bash
# Backend coverage
open coverage/backend/index.html

# Frontend coverage
open coverage/frontend/lcov-report/index.html
```

## Common Tasks

### Debug a Failing Test

```bash
# Run with verbose output
pytest tests/test_models.py -vv

# Run single test
pytest tests/test_models.py::TestServiceModel::test_create_service -vv

# Drop into debugger on failure
pytest --pdb
```

### Run Tests in Watch Mode (Frontend)

```bash
npm run test:watch
```

Tests will automatically re-run when you save files.

### Check Test Coverage

```bash
# Backend
pytest --cov=dashboard --cov-report=term-missing

# Frontend  
npm test -- --coverage
```

### Run Tests by Category

```bash
# Model tests only
pytest -m models

# View tests only
pytest -m views

# API tests only
pytest -m api

# Skip slow tests
pytest -m "not slow"
```

## What Gets Tested?

### Backend (Django/Python)
- ✅ Models: Service, HealthCheck, GrafanaPanel
- ✅ Views: Dashboard, service management, APIs
- ✅ Utilities: Encryption, API client, Traefik sync
- ✅ Integration: Complete workflows

### Frontend (JavaScript)
- ✅ Cookie handling (CSRF tokens)
- ✅ Service refresh functionality
- ✅ Statistics updates
- ✅ API communication
- ✅ DOM manipulation

## Tips for Success

1. **Run tests before committing**:
   ```bash
   ./run_tests.sh
   ```

2. **Write tests for new features**:
   - Add tests to `tests/test_<feature>.py`
   - Follow existing patterns

3. **Keep tests fast**:
   - Use fixtures for setup
   - Mock external API calls
   - Run unit tests frequently

4. **Use CI/CD**:
   - Tests run automatically on push
   - Check GitHub Actions for results

## Need Help?

- 📖 Full Guide: `docs/TESTING.md`
- ⚡ Quick Reference: `docs/TEST_QUICK_REFERENCE.md`
- 📁 Tests Overview: `tests/README.md`
- 📊 Setup Summary: `TESTING_SETUP_SUMMARY.md`

## Next Steps

1. ✅ Run tests: `./run_tests.sh` ← You are here
2. 📖 Read the full testing guide
3. 🔍 Explore test files in `tests/`
4. ✍️ Write tests for your features
5. 🚀 Push to trigger CI/CD tests

Happy testing! 🎉
