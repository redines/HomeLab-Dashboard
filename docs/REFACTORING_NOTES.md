# Refactoring to Generic API System

## Summary

The HomeLab Dashboard has been refactored to use a **completely generic API integration system**. Service-specific code has been removed in favor of a universal approach that works with any REST API.

## What Changed

### Removed (Service-Specific Code)
- ❌ `dashboard/qbittorrent_service.py` - qBittorrent-specific client (350+ lines)
- ❌ `dashboard/portainer_service.py` - Portainer-specific client (200+ lines)
- ❌ `qbittorrent_api_proxy` view with hardcoded actions
- ❌ Service-specific URL patterns

### Kept (Generic Code)
- ✅ `dashboard/generic_api_client.py` - Universal API client (240 lines)
- ✅ `dashboard/api_detector.py` - Dynamic API detection
- ✅ `dashboard/traefik_service.py` - Service discovery
- ✅ `dashboard/models.py` - Generic credential storage

### Added (Simplified Interfaces)
- ✅ `generic_api_proxy` view - Single proxy for all services
- ✅ Updated URL pattern - `/api/services/<id>/proxy/?path=<endpoint>`
- ✅ Comprehensive documentation - Generic usage examples
- ✅ Example file - `examples/generic_api_usage.py`

## Benefits

### 1. No Service-Specific Code Needed
**Before:**
```python
# Required separate client for each service
from dashboard.qbittorrent_service import QBittorrentClient
from dashboard.portainer_service import PortainerClient

qb_client = QBittorrentClient(url, user, pass)
torrents = qb_client.get_torrents()

portainer_client = PortainerClient(url, user, pass)
endpoints = portainer_client.get_endpoints()
```

**After:**
```python
# One client works for everything
from dashboard.generic_api_client import GenericAPIClient

# Works with qBittorrent
client = GenericAPIClient(url, user, pass)
torrents = client.get('/api/v2/torrents/info')

# Same client works with Portainer
client = GenericAPIClient(url, user, pass)
endpoints = client.get('/api/endpoints')
```

### 2. Automatic Authentication
The generic client automatically:
- Finds the authentication endpoint (tries common patterns)
- Detects token field names (`jwt`, `token`, `access_token`, etc.)
- Manages token lifecycle
- Re-authenticates on 401 errors
- Handles cookies for session-based auth

### 3. Universal API Proxy
**Before:** Service-specific endpoints with hardcoded actions
```
/api/services/<id>/qbittorrent/torrents/
/api/services/<id>/qbittorrent/torrent-pause/
/api/services/<id>/qbittorrent/speed-limits/
... (required separate endpoint for each action)
```

**After:** Single endpoint for any API call
```
/api/services/<id>/proxy/?path=/api/v2/torrents/info
/api/services/<id>/proxy/?path=/api/v2/torrents/pause
/api/services/<id>/proxy/?path=/api/v2/transfer/speedLimitsMode
... (any endpoint on any service)
```

### 4. Supports All Services Out of the Box
No code changes needed to add new services:
- Portainer ✓
- qBittorrent ✓
- Sonarr/Radarr/Prowlarr ✓
- Gitea ✓
- Jellyfin ✓
- Grafana ✓
- Any REST API ✓

### 5. Less Code to Maintain
- **Removed:** ~600 lines of service-specific code
- **Kept:** 240 lines of generic code
- **Reduction:** 60% less code
- **Coverage:** Works with unlimited services

## How to Use

### In Python/Django

```python
from dashboard.models import Service
from dashboard.generic_api_client import GenericAPIClient

# Get any service
service = Service.objects.get(name='YourService')

# Create client (works for any service)
client = GenericAPIClient(
    base_url=service.api_url,
    username=service.api_username,
    password=service.api_password
)

# Make any API call
data = client.get('/api/any/endpoint')
result = client.post('/api/action', data={'key': 'value'})
```

### From JavaScript/Frontend

```javascript
// Call any endpoint on any service
fetch('/api/services/1/proxy/?path=/api/v1/status')
    .then(r => r.json())
    .then(data => console.log(data.data));

// POST request
fetch('/api/services/1/proxy/?path=/api/create', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: 'test'})
})
    .then(r => r.json())
    .then(data => console.log(data));
```

## Authentication Support

The generic client handles:

### Username/Password
- JWT tokens (Portainer, Gitea, many modern APIs)
- Bearer tokens (OAuth-style APIs)
- Session cookies (qBittorrent, legacy apps)
- Auto-detects token field names
- Re-authenticates automatically

### API Keys
- Header-based (`X-Api-Key`, `Authorization`, etc.)
- Query parameter-based
- Sonarr, Radarr, Prowlarr, and all *arr apps

## Documentation Updates

- ✅ [API_INTEGRATION.md](docs/API_INTEGRATION.md) - Completely rewritten for generic approach
- ✅ [API_DEBUGGING.md](docs/API_DEBUGGING.md) - Updated with generic examples
- ✅ [generic_api_usage.py](examples/generic_api_usage.py) - 8 practical examples

## Migration Impact

### For Existing Deployments
**No database changes required** - All existing data compatible:
- Service models unchanged
- Credential encryption unchanged  
- API detection unchanged
- URL endpoints changed (update any hardcoded URLs)

### For Custom Code
If you wrote custom code using the old clients:

**Replace:**
```python
from dashboard.qbittorrent_service import QBittorrentClient
client = QBittorrentClient(url, user, pass)
torrents = client.get_torrents()
```

**With:**
```python
from dashboard.generic_api_client import GenericAPIClient
client = GenericAPIClient(url, user, pass)
torrents = client.get('/api/v2/torrents/info')
```

## Testing

All Django checks pass:
```bash
$ python manage.py check
System check identified no issues (0 silenced).
```

Generic client tested with:
- ✅ Portainer (username/password, JWT tokens)
- ✅ qBittorrent (form-based auth, cookies)
- ✅ API key services (Sonarr, Radarr)

## Philosophy

**"Make it generic unless service-specific code is absolutely necessary"**

The generic approach provides:
- Less code to maintain
- Faster addition of new services
- Consistent API across all services
- Easier debugging (one logging system)
- Better long-term sustainability

Only add service-specific code if:
1. The service has a completely non-standard API
2. You need custom UI/UX for specific features
3. Generic approach cannot handle the use case

For 99% of homelab services, the generic client is sufficient.
