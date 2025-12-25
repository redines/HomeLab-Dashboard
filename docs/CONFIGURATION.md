# Configuration Guide

## Environment Variables

Configure the dashboard using environment variables in `.env` file or `docker-compose.yml`.

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Django debug mode | `False` |
| `DJANGO_SECRET_KEY` | Django secret key | (required in production) |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` |
| `TRAEFIK_API_URL` | Traefik API endpoint (optional) | `` |
| `TRAEFIK_API_USERNAME` | Traefik API username (if auth enabled) | `` |
| `TRAEFIK_API_PASSWORD` | Traefik API password (if auth enabled) | `` |
| `SERVICE_REFRESH_INTERVAL` | Auto-refresh interval in seconds | `60` |

**Note**: Traefik configuration is optional. The dashboard automatically detects if Traefik is available and falls back to manual mode if not.

## API Detection

The dashboard automatically detects APIs for your services by probing common API endpoints.

### Automatic Detection

APIs are detected automatically by:
1. **Probing common endpoints** - Tries standard API paths like `/api`, `/api/v1`, `/api/v2`, etc.
2. **Traefik/Docker labels** - Reads API information from container labels
3. **Service names** - Uses the service name as the API type when detected

### Custom API Configuration via Labels

You can provide API information through Docker/Traefik labels to override automatic detection:

```yaml
services:
  myservice:
    image: myapp:latest
    labels:
      # Enable API detection
      - "homelab.api.enabled=true"
      # Specify API type
      - "homelab.api.type=myapp"
      # Docker Compose service name is also used
      - "com.docker.compose.service=myservice"
```

### Manual API Configuration

For services requiring authentication or custom API endpoints, configure credentials in the service detail page:
- Navigate to the service in the dashboard
- Click "Configure API"
- Enter API credentials (stored encrypted)
- API URL is auto-populated from Traefik but can be edited

### API Re-detection

- APIs are cached for 7 days to avoid unnecessary probing
- After 5 failed detection attempts, probing is throttled to every 5 minutes
- Force re-detection via CLI: `python manage.py detect_apis --force`
- Force re-detection via UI: Click "Re-detect API" button on service detail page
- Regular refresh respects throttling to reduce network traffic

## Traefik Configuration

Ensure your Traefik instance has the API enabled.

### Basic Configuration (Development)

Add to your `traefik.yml`:

```yaml
api:
  dashboard: true
  insecure: true  # Only for testing! Use authentication in production
```

Or via command line:
```yaml
--api.dashboard=true
--api.insecure=true
```

### Production Configuration

For production, enable authentication:

```yaml
api:
  dashboard: true

http:
  middlewares:
    auth:
      basicAuth:
        users:
          - "admin:$apr1$xyz..."  # htpasswd generated hash
```

Then set the credentials in your dashboard environment:
```bash
TRAEFIK_API_USERNAME=admin
TRAEFIK_API_PASSWORD=your-password
```

## Usage

### Admin Panel

Access the Django admin at `http://localhost:8000/admin` to:
- Manually add/edit services
- View service health history
- Manage service metadata and tags

### Management Commands

**Sync services from Traefik:**
```bash
python manage.py sync_services
```

**Run database migrations:**
```bash
python manage.py migrate
```

**Create superuser:**
```bash
python manage.py createsuperuser
```

### API Endpoints

- `GET /api/services/` - List all services as JSON
- `POST /api/services/refresh/` - Refresh services from Traefik and check health
- `POST /api/services/<id>/health/` - Check health of a specific service

## Customization

### Adding Service Icons

Edit a service in the admin panel and set the `icon` field to an emoji or icon class:
- Emojis: `🌐`, `🗄️`, `📊`, `🔐`, etc.
- Font Awesome (if added): `fas fa-server`, `fas fa-database`, etc.

### Custom Service Types

The dashboard supports these service types out of the box:
- Docker
- Kubernetes
- Virtual Machine
- Bare Metal
- Other

Edit services in the admin panel to set the appropriate type.

### Styling

Modify `static/css/style.css` to customize the look and feel:
- Color scheme (CSS variables at the top)
- Card layouts
- Animations and transitions

## Troubleshooting

### Services not appearing

1. Check Traefik API is accessible:
   ```bash
   curl http://your-traefik-host:8080/api/http/routers
   ```

2. Verify environment variables in `.env` or `docker-compose.yml`

3. Check Django logs:
   ```bash
   docker-compose logs web
   ```

4. Manually sync services:
   ```bash
   docker-compose exec web python manage.py sync_services
   ```

### Connection errors

- Ensure the dashboard can reach Traefik (network connectivity)
- Check if Traefik API requires authentication
- Verify TRAEFIK_API_URL is correct
- Test the URL manually: `curl http://your-traefik-url/api/http/routers`

### Permission issues in Docker

If you encounter permission issues with SQLite database:
```bash
docker-compose exec web chown -R appuser:appuser /app
```

### Health checks failing

- Verify services are actually running
- Check if services require authentication
- Ensure services are accessible from the dashboard container
- Review service URLs in the admin panel

### No data showing after sync

- Check that Traefik has routers configured
- Verify router rules contain URLs
- Look at Django logs for errors during sync
- Try manually adding a service in admin panel

## Production Deployment

For production use:

### 1. Set a strong SECRET_KEY

Generate a new secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Add to your environment:
```env
DJANGO_SECRET_KEY=your-generated-secret-key
```

### 2. Disable DEBUG

```env
DEBUG=False
```

### 3. Configure ALLOWED_HOSTS

```env
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 4. Use PostgreSQL instead of SQLite (recommended)

Update `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'homelab_dashboard'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

Add to requirements:
```txt
psycopg2-binary
```

### 5. Setup HTTPS with Traefik

Add labels to your docker-compose.yml:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.dashboard.rule=Host(`dashboard.yourdomain.com`)"
  - "traefik.http.routers.dashboard.entrypoints=websecure"
  - "traefik.http.routers.dashboard.tls.certresolver=letsencrypt"
```

### 6. Enable Traefik API authentication

See Traefik Configuration section above.

### 7. Setup periodic sync with cron or systemd timer

**Cron example:**
```bash
# Run sync every 5 minutes
*/5 * * * * docker-compose exec -T web python manage.py sync_services >> /var/log/homelab-sync.log 2>&1
```

**Systemd timer example:**

Create `/etc/systemd/system/homelab-sync.service`:
```ini
[Unit]
Description=HomeLab Dashboard Service Sync

[Service]
Type=oneshot
WorkingDirectory=/path/to/HomeLab-Dashboard
ExecStart=/usr/bin/docker-compose exec -T web python manage.py sync_services
```

Create `/etc/systemd/system/homelab-sync.timer`:
```ini
[Unit]
Description=Run HomeLab Dashboard sync every 5 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable homelab-sync.timer
sudo systemctl start homelab-sync.timer
```

### 8. Setup static file serving

For production, collect static files:
```bash
python manage.py collectstatic --noinput
```

Configure a web server (nginx) to serve static files:
```nginx
location /static/ {
    alias /path/to/HomeLab-Dashboard/staticfiles/;
}
```

### 9. Use a process manager

Use gunicorn or uwsgi instead of Django's development server:

```bash
pip install gunicorn
gunicorn homelab_dashboard.wsgi:application --bind 0.0.0.0:8000
```

### 10. Setup monitoring and logging

- Configure Django logging to file
- Setup log rotation
- Consider using Sentry for error tracking
- Monitor container health with Docker healthchecks
