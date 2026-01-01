# API Debugging Guide

## Overview

The HomeLab Dashboard includes a **generic API client** that works with any service. No service-specific code is needed - the client automatically handles authentication and requests for all your homelab services.

## Generic API Client

The `GenericAPIClient` is designed to work with any REST API. It supports:
- Username/password authentication (JWT, Bearer tokens, cookies)
- API key authentication (via headers or query parameters)
- All HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Automatic authentication retry on 401
- Comprehensive logging for debugging

## Viewing API Logs

### Enable Debug Logging

To see detailed API logs, set your Django logging level to DEBUG in your environment or settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'dashboard': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Set to DEBUG for detailed logs
            'propagate': False,
        },
    },
}
```

### What Gets Logged

#### Authentication Logs (INFO level)
- ✓ Successful authentication
- ✗ Failed authentication with reason
- Authentication endpoint URL
- Username being used (password is never logged)

#### Request Logs (DEBUG level)
- HTTP method and full URL
- Request parameters, data, and JSON body
- Response status code and headers
- Response body (first 500 characters)
- Token information (sanitized)

#### Error Logs (ERROR level)
- Connection errors with details
- Timeout errors
- HTTP errors with status codes and response text
- SSL/TLS errors
- Authentication failures with specific reasons

## Testing API Connections

### Using Django Shell

Test any service API directly with the generic client:

```python
python manage.py shell

from dashboard.models import Service
from dashboard.utils.generic_api_client import GenericAPIClient

# Get your service
service = Service.objects.get(name='Portainer')  # Or any service name

# Create generic client with username/password
client = GenericAPIClient(
    base_url=service.api_url,
    username=service.api_username,
    password=service.api_password
)

# Authenticate (optional - automatically called on first request)
client.authenticate()

# Make API requests
status = client.get('/api/status')
print(status)

# POST request
result = client.post('/api/endpoint', data={'key': 'value'})

# For services using API keys instead
client = GenericAPIClient(
    base_url='https://sonarr.local',
    api_key='your-api-key-here'
)
data = client.get('/api/v3/system/status')
```

### Using the Generic API Proxy

Call any service API from your frontend JavaScript or other clients:

```javascript
// GET request to any endpoint
fetch('/api/services/1/proxy/?path=/api/v1/status')
    .then(response => response.json())
    .then(data => console.log(data.data));

// POST request
fetch('/api/services/1/proxy/?path=/api/v1/action', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({key: 'value'})
})
    .then(response => response.json())
    .then(data => console.log(data.data));
```

**URL Format:** `/api/services/<service_id>/proxy/?path=<target_endpoint>`

- `service_id`: The database ID of the service
- `path`: The API endpoint path (e.g., `/api/torrents/info`, `/api/v1/status`)

The proxy automatically:
- Adds authentication (username/password or API key)
- Forwards your HTTP method (GET, POST, PUT, DELETE, PATCH)
- Forwards query parameters (except `path`)
- Forwards request body
- Returns the API response as JSON

## Common Issues and Solutions
Most services auto-detect the auth endpoint from common patterns
2. If your service uses a non-standard endpoint, specify it when creating the client:
   ```python
   client = GenericAPIClient(
       base_url='https://service.local',
       username='admin',
       password='password',
       auth_endpoint='/custom/auth/path'  # Override default
   )
   ```
3. Common endpoints the client tries automatically:
   - `/api/auth`
   - `/api/login`
   - `/auth/login`
   - `/login`

**Solutions:**
1. Verify credentials in service detail page
2. Check if the account is locked or disabled
3. Ensure username is case-sensitive correct
4. Try logging in directly to the service UI to verify credentials

### Issue: "Authentication endpoint not found"

**Logs show:**
```
ERROR ✗ Authentication endpoint not found: https://service/api/auth
```

**Solutions:**
1. Check the service API documentation for correct auth endpoint
2. Common endpoints:
   - `/api/auth` (Portainer, many REST APIs)
   - `/api/v2/auth/login` (qBittorrent)
   - `/api/login`
   - `/auth/login`
3. Update the `auth_endpoint` parameter when creating the client

### Issue: "Connection timeout"

**Logs show:**
```
ERROR ✗ Request timeout: URL did not respond within 10 seconds
```

**Solutions:**
1. Check if service is running
2. Verify network connectivity
3. Check firewall rules
4. Ensure URL is correct (check for typos)

### Issue: "Access forbidden (403)"

**Logs show:**
```
ERROR ✗ Authentication failed: Access forbidden
```

**Solutions:**
1. Check IP whitelist settings in service
2. Verify user has API access permissions
3. Check if API access is enabled in service settings
4. Review service-specific access control lists

### Issue: "SSL/TLS certificate error"

**Logs show:**
```
ERROR ✗ SSL error: certificate verify failed
```

**Solutions:**
1. For self-signed certificates, the client already sets `verify=False`
2. If still failing, check if the certificate is properly configured
3. Try accessing the service URL in a browser to see SSL details

###The client automatically handles:
   - JWT tokens in response JSON (`jwt`, `token`, `access_token`, `auth_token` fields)
   - Cookie-based authentication (session cookies)
   - Bearer tokens in headers
2. If your service uses a non-standard token field, the client will still work with cookies
3. Service-Specific Notes

### Services Using API Keys (Sonarr, Radarr, Prowlarr, etc.)

These services don't require authentication - just include the API key:

```python
client = GenericAPIClient(
    base_url='https://sonarr.local',
    api_key='your-api-key-here'
)

# API key is automatically added to X-Api-Key header
system_status = client.get('/api/v3/system/status')
```

Get the API key from: **Settings → General → Security → API Key**

### Services Using Username/Password

Most services with web UIs use this method:

```python
client = GenericAPIClient(
    base_url='https://portainer.local',
    username='admin',
    password='your-password'
)

# Client automatically authenticates and manages tokens
status = client.get('/api/status')
```

The client automatically:
- Detects the authentication endpoint
- Finds the token in the response
- Adds the token to subsequent requests
- Re-authenticates on 401 errors
- **Auth endpoint:** `/api/v2/auth/login`
- **Auth method:** Form data (not JSON)
- **Response:** Plain text "Ok." on success
- **Session:** Cookie-based (SID)
- **Docs:** https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API

### Sonarr/Radarr/Prowlarr/*arr
- **Auth method:** API key in `X-Api-Key` header
- **No login required:** Just include API key in every request
- **Get API key:** Settings → General → Security → API Key

## Enabling Verbose Logging Temporarily

For one-time debugging, set environment variable:

```bash
export DJANGO_LOG_LEVEL=DEBUG
python manage.py runserver
```

Or in Django shell:

```python
import logging
logging.getLogger('dashboard').setLevel(logging.DEBUG)
```

## Reading the Logs

### Successful Request Flow
```
INFO  Attempting authentication at https://portainer.local/api/auth
DEBUG Using username: admin
DEBUG Auth response - Status: 200
DEBUG Auth response body: {"jwt": "eyJ..."}
INFO  ✓ Successfully authenticated and obtained token
INFO  Making GET request to https://portainer.local/api/status
DEBUG Response status: 200
DEBUG Successfully parsed JSON response with keys: ['Version', 'InstanceID']
```

### Failed Authentication Flow
```
INFO  Attempting authentication at https://portainer.local/api/auth
DEBUG Using username: admin
DEBUG Auth response - Status: 401
DEBUG Auth response body: {"message": "Invalid credentials"}
ERROR ✗ Authentication failed: Invalid username or password
ERROR Response: {"message": "Invalid credentials"}
```

## Getting Help

When reporting API issues, include:
1. Service name and version
2. Complete error logs (with DEBUG enabled)
3. API endpoint being called
4. Expected vs actual behavior
5. Screenshots of service API documentation if available
