# Quick Reference: Manual Service Management

## Environment Variables

```bash
# Traefik integration (automatic detection)
# Leave empty or unset for manual-only mode
TRAEFIK_API_URL=http://traefik:8080/api
TRAEFIK_API_USERNAME=your_username  # Optional
TRAEFIK_API_PASSWORD=your_password  # Optional

# App automatically detects if Traefik is available
# No manual enable/disable needed!
```

## API Endpoints

### Create Service
```http
POST /api/services/create/
Content-Type: application/json

{
  "name": "Service Name",
  "url": "service.com",  // Flexible: protocol auto-added, IPs/ports supported
  "description": "Optional description",
  "icon": "🔧",
  "service_type": "docker",
  "provider": "local",  // or "external"
  "tags": "tag1, tag2"
}
```

### Update Service
```http
POST /api/services/<id>/update/
Content-Type: application/json

{
  "name": "Updated Name",
  "url": "https://updated-url.com",
  ...
}
```

### Delete Service
```http
POST /api/services/<id>/delete/
```

### Refresh Services
```http
POST /api/services/refresh/

Response:
{
  "success": true,
  "synced_services": 5,
  "health_checks": 10,
  "traefik_enabled": true,
  "traefik_available": true,
  "warning": "..."  // If Traefik unavailable
}
```

## Service Types

| Type | Use For |
|------|---------|
| `docker` | Docker containers |
| `kubernetes` | Kubernetes pods/services |
| `vm` | Virtual machines |
| `bare_metal` | Physical servers |
| `external` | External websites (Google, GitHub, etc.) |
| `other` | Everything else |

## Provider Types

| Provider | Description |
|----------|-------------|
| `local` | Manually added service in your homelab |
| `external` | External service (not in homelab) |
| `traefik` | Auto-discovered from Traefik |

## UI Actions

### Add Service
1. Click "➕ Add Service" button in header
2. Fill in form fields
3. Click "Add Service"

### Edit Service (Manual Only)
1. Click service card
2. Click "✏️ Edit" button
3. Update fields
4. Click "Update Service"

### Delete Service (Manual Only)
1. Click service card
2. Click "🗑️ Delete" button
3. Confirm deletion

### Refresh Services
1. Click "🔄 Refresh Services" button
2. Traefik services synced (if enabled)
3. Health checks performed
4. Page reloads with updated data

## Database Model

```python
class Service(models.Model):
    # Required fields
    name = models.CharField(max_length=255, unique=True)
    url = models.URLField(max_length=500)
    
    # Type and provider
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)
    provider = models.CharField(max_length=100, choices=PROVIDER_CHOICES)
    is_manual = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(max_length=20, choices=SERVICE_STATUS_CHOICES)
    last_checked = models.DateTimeField(null=True, blank=True)
    response_time = models.IntegerField(null=True, blank=True)
    
    # Optional fields
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=500, blank=True)
    
    # API integration
    api_url = models.URLField(max_length=500, blank=True)
    api_type = models.CharField(max_length=50, blank=True)
    # ... (encrypted fields)
```

## Common Tasks

### Run without Traefik
```bash
# 1. Set environment variable
echo "TRAEFIK_ENABLED=False" >> .env

# 2. Restart
docker-compose restart

# 3. Add services manually via UI
```

### Switch from Traefik to Manual
```bash
# 1. Export current services (optional)
python manage.py dumpdata dashboard.Service > services_backup.json

# 2. Disable Traefik
echo "TRAEFIK_ENABLED=False" >> .env

# 3. Restart
docker-compose restart

# 4. Manually re-add important services via UI
```

### Mixed Mode (Recommended)
```bash
# 1. Keep Traefik enabled (default)
TRAEFIK_ENABLED=True

# 2. Add additional manual services via UI
# 3. Both types coexist peacefully
```

## Health Check Status Codes

| Status | HTTP Codes | Meaning |
|--------|------------|---------|
| 🟢 Up | 200-299, 3xx, 401, 403, 405 | Service responding |
| 🔴 Down | 404, 5xx, timeout, connection error | Service not responding |
| 🟡 Unknown | - | Not checked yet |

## Troubleshooting

### "Traefik is enabled but not available"
- Check Traefik is running
- Verify TRAEFIK_API_URL
- Check authentication credentials
- Or disable: `TRAEFIK_ENABLED=False`

### Cannot edit/delete service
- Only manual services can be edited
- Traefik services are read-only
- Check if service has `is_manual=True`

### Service always shows as down
- Verify URL is correct
- Check network connectivity
- Service might require authentication
- Check browser console for errors

### Duplicate service name error
- Service names must be unique
- Choose a different name
- Or delete/edit existing service

## Migration Commands

```bash
# Create migration
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations

# Rollback (if needed)
python manage.py migrate dashboard 0006
```

## Docker Commands

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate

# Access shell
docker-compose exec web python manage.py shell

# Restart
docker-compose restart

# Stop
docker-compose down
```

## Examples

### Add Homelab Service
```json
{
  "name": "Plex",
  "url": "https://plex.example.com",
  "description": "Media server",
  "icon": "🎬",
  "service_type": "docker",
  "provider": "manual",
  "tags": "media, streaming"
}
```

### Add External Service
```json
{
  "name": "GitHub",
  "url": "https://github.com",
  "description": "Code repository",
  "icon": "🐙",
  "service_type": "external",
  "provider": "external",
  "tags": "development, git"
}
```

### Add Local Network Service
```json
{
  "name": "Router Admin",
  "url": "http://192.168.1.1",
  "description": "Router configuration",
  "icon": "🌐",
  "service_type": "other",
  "provider": "manual",
  "tags": "network, admin"
}
```
