# Project Organization

This document describes how the project is organized after the recent restructuring for better maintainability.

## Directory Structure

```
HomeLab-Dashboard/
├── dashboard/              # Main Django app
│   ├── utils/             # Utility modules
│   │   ├── encryption.py          # Credential encryption
│   │   ├── api_detector.py        # API detection logic
│   │   ├── traefik_service.py     # Traefik integration
│   │   └── generic_api_client.py  # Generic API client
│   ├── pages/             # Feature-specific modules (planned)
│   │   ├── home/          # Dashboard home page
│   │   ├── services/      # Service management
│   │   ├── service_api/   # API integration
│   │   ├── grafana/       # Grafana panels
│   │   └── health/        # Health checks
│   ├── management/        # Django management commands
│   ├── migrations/        # Database migrations
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # URL routing
│   └── admin.py           # Admin interface
│
├── docs/                  # All documentation
│   ├── WELCOME.md                  # Getting started guide
│   ├── QUICKSTART.md               # Quick setup guide
│   ├── TESTING_QUICKSTART.md       # Testing guide
│   ├── TESTING_SETUP_SUMMARY.md    # Testing setup overview
│   └── ... (other docs)
│
├── scripts/               # Utility scripts
│   ├── run_tests.sh      # Test runner
│   ├── start.sh          # Development startup
│   └── test-setup.sh     # Setup verification
│
├── templates/             # Django templates
│   ├── base.html
│   └── dashboard/        # Dashboard-specific templates
│
├── tests/                 # All test files
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_utilities.py
│   ├── test_integration.py
│   └── frontend/         # Frontend tests
│
├── static/                # Static files (CSS, JS)
├── examples/              # Example code
└── homelab_dashboard/     # Django project settings

```

## Key Changes

### 1. Moved Markdown Documentation to `docs/`
All markdown documentation files have been consolidated in the `docs/` directory:
- `TESTING_QUICKSTART.md` → `docs/TESTING_QUICKSTART.md`
- `TESTING_SETUP_SUMMARY.md` → `docs/TESTING_SETUP_SUMMARY.md`

### 2. Organized Scripts into `scripts/`
All shell scripts are now in a dedicated `scripts/` directory:
- `run_tests.sh` → `scripts/run_tests.sh`
- `start.sh` → `scripts/start.sh`
- `test-setup.sh` → `scripts/test-setup.sh`

### 3. Created `dashboard/utils/` for Utility Modules
Utility modules have been moved to `dashboard/utils/`:
- `encryption.py` → `dashboard/utils/encryption.py`
- `api_detector.py` → `dashboard/utils/api_detector.py`
- `traefik_service.py` → `dashboard/utils/traefik_service.py`
- `generic_api_client.py` → `dashboard/utils/generic_api_client.py`

## Import Changes

If you're extending the project, update your imports:

**Old:**
```python
from dashboard.encryption import EncryptedCharField
from dashboard.generic_api_client import GenericAPIClient
from dashboard.traefik_service import sync_traefik_services
from dashboard.api_detector import APIDetector
```

**New:**
```python
from dashboard.utils.encryption import EncryptedCharField
from dashboard.utils.generic_api_client import GenericAPIClient
from dashboard.utils.traefik_service import sync_traefik_services
from dashboard.utils.api_detector import APIDetector
```

## Running Scripts

All scripts are now in the `scripts/` directory:

```bash
# Run tests
./scripts/run_tests.sh

# Start development server
./scripts/start.sh

# Verify setup
./scripts/test-setup.sh
```

## Future Organization (Planned)

The `dashboard/pages/` directory structure has been created for future reorganization of views:
- Each feature/page will have its own subdirectory
- Related views, forms, and utilities will be co-located
- This will make the codebase more modular and maintainable

## Benefits

1. **Cleaner Root Directory**: Essential files are easier to find
2. **Better Organization**: Related files are grouped together
3. **Easier Navigation**: Logical structure makes development faster
4. **Improved Maintainability**: Modular structure scales better
5. **Clear Separation**: Documentation, scripts, and code are clearly separated

## Migration Notes

All imports have been updated throughout the project:
- ✅ Tests updated
- ✅ Views updated
- ✅ Management commands updated
- ✅ Documentation updated
- ✅ Templates updated

No user-facing changes - the application works exactly the same way!
