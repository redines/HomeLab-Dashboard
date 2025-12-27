# API Integration Guide## OverviewThe HomeLab Dashboard provides a **generic API integration system** that works with any REST API service without requiring service-specific code. The system automatically detects APIs, manages authentication, and provides a unified interface for all your homelab services.## Features- **Universal Compatibility**: Works with any REST API- **Automatic Detection**: Scans services for API availability- **Multiple Auth Methods**: Username/password (JWT, Bearer tokens, cookies) or API keys- **Encrypted Storage**: Credentials encrypted with Fernet symmetric encryption- **Generic Proxy**: Single endpoint to access any service API- **Comprehensive Logging**: Detailed logs for debugging- **Smart Caching**: Reduces repeated API detection overhead## Quick Start### 1. Sync Services from Traefik```bashpython manage.py sync_traefik```This discovers services and automatically detects APIs.### 2. Configure CredentialsVisit any service detail page and add credentials:**For username/password services (Portainer, qBittorrent, etc.):**- API URL: Auto-populated from service URL- Username: Your login username- Password: Your login password**For API key services (Sonarr, Radarr, Prowlarr, etc.):**- API URL: Auto-populated from service URL- API Key: Find in service settings (usually Settings → General → Security)### 3. Use the API**Python/Django:**```pythonfrom dashboard.models import Servicefrom dashboard.utils.generic_api_client import GenericAPIClientservice = Service.objects.get(name='Portainer')client = GenericAPIClient(    base_url=service.api_url,    username=service.api_username,    password=service.api_password)# Make requestsstatus = client.get('/api/status')data = client.post('/api/endpoint', data={'key': 'value'})```**JavaScript/Frontend:**```javascript// GET requestconst response = await fetch('/api/services/1/proxy/?path=/api/status');const data = await response.json();// POST requestconst response = await fetch('/api/services/1/proxy/?path=/api/action', {    method: 'POST',    headers: {'Content-Type': 'application/json'},    body: JSON.stringify({key: 'value'})});```## Generic API ClientThe `GenericAPIClient` class handles all API interactions:### Features- **Auto-authentication**: Automatically finds auth endpoints and obtains tokens- **Token management**: Stores and reuses tokens across requests- **Smart retry**: Re-authenticates on 401 errors- **Multiple auth types**: JWT, Bearer tokens, API keys, session cookies- **All HTTP methods**: GET, POST, PUT, DELETE, PATCH- **Flexible data formats**: JSON, form data, raw strings### Creating a Client**With username and password:**```pythonclient = GenericAPIClient(    base_url='https://service.local',    username='admin',    password='password')```**With API key:**```pythonclient = GenericAPIClient(    base_url='https://service.local',    api_key='your-api-key-here')```**With custom auth endpoint:**```pythonclient = GenericAPIClient(    base_url='https://service.local',    username='admin',    password='password',    auth_endpoint='/custom/login'  # Override default)```### Making Requests```python# GET requestdata = client.get('/api/endpoint')# GET with query parametersdata = client.get('/api/torrents', params={'filter': 'downloading'})# POST with JSONresult = client.post('/api/create', data={'name': 'test'})# PUT requestclient.put('/api/update/123', data={'status': 'active'})# DELETE requestclient.delete('/api/delete/123')# Raw request with full controlresponse = client.request(    method='POST',    endpoint='/api/custom',    data={'key': 'value'},    params={'param': 'value'})```## API Proxy EndpointThe proxy provides HTTP access to any service API:**Endpoint:** `/api/services/<service_id>/proxy/?path=<target_path>`### Parameters- `service_id`: Database ID of the service (from URL or service list)- `path`: Target API endpoint (query parameter)- Additional query parameters are forwarded to the service### Examples**GET request:**```bashcurl "http://localhost:8000/api/services/1/proxy/?path=/api/status"```**POST request:**```bashcurl -X POST \  "http://localhost:8000/api/services/1/proxy/?path=/api/create" \  -H "Content-Type: application/json" \  -d '{"name": "test"}'```**With query parameters:**```bashcurl "http://localhost:8000/api/services/1/proxy/?path=/api/torrents&filter=downloading&category=movies"```### Response FormatSuccess:```json{  "success": true,  "data": {    "...": "API response data"  }}```Error:```json{  "success": false,  "error": "Error message"}```## API Detection### Automatic DetectionAPIs are automatically detected when services are synced:```bashpython manage.py sync_traefik```### Detection MethodsThe system uses multiple methods (in order):1. **Traefik Labels**   - `homelab.api.enabled=true`: Mark service as having an API   - `homelab.api.type=servicename`: Specify service type   - `homelab.api.endpoint=/api`: Specify API path2. **Service Name Matching**   - Recognizes common homelab services: portainer, qbittorrent, sonarr, radarr, prowlarr, lidarr, readarr, bazarr, sabnzbd, nzbget, transmission, deluge, jellyfin, plex, emby, tautulli, overseerr, requestrr, ombi, calibre-web, paperless, nextcloud, syncthing, gitea, drone, jenkins, gitlab, grafana, prometheus, heimdall, organizr, traefik, etc.3. **Endpoint Probing**   - Tests 19 common API paths:     - `/api`, `/api/v1`, `/api/v2`, `/api/v3`     - `/api/status`, `/api/system/status`, `/api/health`     - `/api/version`, `/api/ping`     - Service-specific paths### Manual Re-detection**Via UI:**1. Go to service detail page2. Click "Re-detect API" button**Via CLI:**```bash# Re-detect all servicespython manage.py detect_apis --force# Sync Traefik and detect APIspython manage.py sync_traefik```### Caching- Detection results cached for **7 days**- Use `--force` flag or "Re-detect API" button to bypass cache- Reduces overhead on Traefik API and service endpoints## Authentication Types### Username/Password (JWT/Bearer Tokens)Most modern web services use this method:**Services:** Portainer, Gitea, qBittorrent, many custom APIs**How it works:**1. Client POSTs credentials to auth endpoint2. Service returns JWT or Bearer token3. Client includes token in `Authorization: Bearer <token>` header4. Client re-authenticates automatically on 401 errors**Common endpoints tried:**- `/api/auth`- `/api/login`- `/auth/login`
- `/login`

### Session Cookies

Some services use cookie-based authentication:

**Services:** qBittorrent, some older web apps

**How it works:**
1. Client POSTs credentials to login endpoint
2. Service sets session cookie
3. Client includes cookie in subsequent requests
4. Generic client handles this automatically

### API Keys

Simpler services use API key authentication:

**Services:** Sonarr, Radarr, Prowlarr, Lidarr, Readarr, Bazarr, and most *arr apps

**How it works:**
1. No login required
2. Include API key in `X-Api-Key` header (or as configured)
3. All requests authenticated immediately

**Finding API keys:**
- Usually in: Settings → General → Security → API Key
- Or: Settings → API → API Key

## Security

### Credential Encryption

All credentials are encrypted using Fernet symmetric encryption:

- **Algorithm**: AES-128-CBC with HMAC authentication
- **Key generation**: Automatic on first use
- **Key storage**: `~/.homelab-dashboard/encryption.key`
- **Key permissions**: 600 (read/write for owner only)

See [ENCRYPTED_CREDENTIALS.md](ENCRYPTED_CREDENTIALS.md) for details.

### Best Practices

1. **Use HTTPS**: Always use HTTPS for API URLs when possible
2. **Unique credentials**: Create separate API users with limited permissions
3. **API keys**: Prefer API keys over username/password when available
4. **Read-only access**: Use read-only API keys when only viewing data
5. **Regular rotation**: Rotate API keys periodically

## Troubleshooting

### Enable Debug Logging

Set logging level to DEBUG to see detailed API logs:

```bash
export DJANGO_LOG_LEVEL=DEBUG
python manage.py runserver
```

Or in Django shell:
```python
import logging
logging.getLogger('dashboard').setLevel(logging.DEBUG)
```

### Common Issues

**"Invalid username or password"**
- Verify credentials in service UI
- Check if username is case-sensitive
- Ensure account is not locked

**"Authentication endpoint not found"**
- Service may use non-standard endpoint
- Specify custom `auth_endpoint` when creating client
- Check service API documentation

**"Connection refused"**
- Verify service is running
- Check API URL is correct
- Ensure no firewall blocking requests

**"SSL certificate error"**
- Client automatically uses `verify=False` for self-signed certificates
- Ensure certificate is properly configured in service

See [API_DEBUGGING.md](API_DEBUGGING.md) for detailed troubleshooting guide.

## Examples

### Portainer

```python
# Get endpoints
client = GenericAPIClient(
    base_url='https://portainer.local',
    username='admin',
    password='password'
)
endpoints = client.get('/api/endpoints')

# Get stacks
stacks = client.get('/api/stacks')

# Create stack
new_stack = client.post('/api/stacks', data={
    'Name': 'mystack',
    'SwarmID': '',
    'StackFileContent': 'version: "3"\n...'
})
```

### Sonarr/Radarr/*arr

```python
# Get system status
client = GenericAPIClient(
    base_url='https://sonarr.local',
    api_key='your-api-key-here'
)
status = client.get('/api/v3/system/status')

# Get calendar
calendar = client.get('/api/v3/calendar')

# Search for series
results = client.get('/api/v3/series/lookup', params={'term': 'Breaking Bad'})
```

### qBittorrent

```python
# Get torrents
client = GenericAPIClient(
    base_url='http://qbittorrent.local:8080',
    username='admin',
    password='adminadmin'
)
torrents = client.get('/api/v2/torrents/info')

# Add torrent
client.post('/api/v2/torrents/add', data={
    'urls': 'magnet:?xt=urn:...'
})

# Pause torrent
client.post('/api/v2/torrents/pause', data={
    'hashes': 'torrent_hash_here'
})
```

### Gitea

```python
# Get repositories
client = GenericAPIClient(
    base_url='https://gitea.local',
    username='user',
    password='password'
)
repos = client.get('/api/v1/user/repos')

# Create repository
new_repo = client.post('/api/v1/user/repos', data={
    'name': 'new-repo',
    'description': 'My new repository',
    'private': True
})
```

## Architecture

### Components

1. **GenericAPIClient** (`dashboard/generic_api_client.py`)
   - Universal API client
   - Handles authentication and requests
   - 240 lines, fully documented

2. **Service Model** (`dashboard/models.py`)
   - Encrypted credential fields
   - API detection flags and cache

3. **API Detector** (`dashboard/api_detector.py`)
   - Detection logic
   - Endpoint probing
   - Label reading

4. **Views** (`dashboard/views.py`)
   - `generic_api_proxy`: HTTP proxy endpoint
   - `service_api_docs`: API documentation
   - `detect_service_api`: Manual re-detection

5. **Management Commands** (`dashboard/management/commands/`)
   - `sync_traefik`: Sync services and detect APIs
   - `detect_apis`: Re-detect APIs for all services

### Flow Diagram

```
User Request
    ↓
Generic API Proxy View
    ↓
Get Service from Database
    ↓
Create GenericAPIClient with credentials
    ↓
Client authenticates (if needed)
    ↓
Client makes request to service API
    ↓
Response returned to user
```

## Future Enhancements

Potential improvements (not currently needed):

- API rate limiting
- Request caching
- Webhook support
- Service-specific UI dashboards (only if really needed)
- API usage statistics
- Response transformation/normalization

The current generic approach should handle all common use cases without service-specific code.
