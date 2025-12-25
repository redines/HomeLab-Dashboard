# Project Structure

```
HomeLab-Dashboard/
│
├── 📄 manage.py                      # Django management script
├── 📄 start.sh                       # Development startup script
├── 📄 requirements.txt               # Python dependencies
├── 📄 Dockerfile                     # Docker container definition
├── 📄 docker-compose.yml             # Docker Compose configuration
├── 📄 .env.example                   # Example environment variables
├── 📄 .gitignore                     # Git ignore rules
├── 📄 .dockerignore                  # Docker ignore rules
├── 📄 README.md                      # Complete documentation
├── 📄 QUICKSTART.md                  # Quick start guide
├── 📄 STRUCTURE.md                   # This file
├── 📄 LICENSE                        # License file
└── 📄 traefik-example.yml            # Example Traefik configuration
│
├── 📁 homelab_dashboard/             # Django project configuration
│   ├── __init__.py
│   ├── settings.py                   # Main Django settings
│   ├── urls.py                       # Root URL configuration
│   ├── wsgi.py                       # WSGI application
│   └── asgi.py                       # ASGI application
│
├── 📁 dashboard/                     # Main dashboard application
│   ├── __init__.py
│   ├── apps.py                       # App configuration
│   ├── models.py                     # Database models (Service, HealthCheck)
│   ├── views.py                      # Views and API endpoints
│   ├── urls.py                       # Dashboard URL routing
│   ├── admin.py                      # Django admin configuration
│   ├── traefik_service.py           # Traefik API integration
│   │
│   └── 📁 management/                # Django management commands
│       ├── __init__.py
│       └── 📁 commands/
│           ├── __init__.py
│           └── sync_services.py      # Sync services from Traefik
│
├── 📁 templates/                     # HTML templates
│   ├── base.html                     # Base template with header/footer
│   └── 📁 dashboard/
│       └── index.html                # Main dashboard page
│
├── 📁 static/                        # Static files (CSS, JavaScript)
│   ├── 📁 css/
│   │   └── style.css                 # Main stylesheet
│   └── 📁 js/
│       └── dashboard.js              # Dashboard JavaScript
│
└── 📁 staticfiles/                   # Collected static files (generated)
```

## Key Components

### Backend (Django)

- **homelab_dashboard/**: Project configuration and settings
- **dashboard/**: Main application with models, views, and Traefik integration
- **traefik_service.py**: Service discovery and API communication with Traefik

### Frontend

- **templates/**: Jinja2 HTML templates
- **static/**: CSS and JavaScript files
- **Modern UI**: Dark theme with card-based layout

### Database Models

1. **Service**: Stores discovered services with metadata
   - name, url, status, service_type, provider
   - health metrics (uptime, response_time)
   - Traefik metadata (router_name, service_name)

2. **HealthCheck**: Historical health check records
   - status, response_time, checked_at
   - error messages

### API Endpoints

- `GET /` - Main dashboard view
- `GET /api/services/` - List all services (JSON)
- `POST /api/services/refresh/` - Refresh from Traefik
- `POST /api/services/<id>/health/` - Check service health

### Management Commands

- `sync_services` - Sync services from Traefik API
- Standard Django commands (migrate, createsuperuser, etc.)

## Technology Stack

- **Backend**: Django 5.1 (Python 3.12)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: SQLite (development) / PostgreSQL (recommended for production)
- **Server**: Gunicorn (production) / Django dev server (development)
- **Container**: Docker with Docker Compose
- **Integration**: Traefik API for service discovery

## File Purposes

| File | Purpose |
|------|---------|
| `manage.py` | Django CLI management tool |
| `start.sh` | Quick development environment setup |
| `requirements.txt` | Python package dependencies |
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Multi-container setup |
| `.env.example` | Environment variable template |
| `settings.py` | Django configuration |
| `models.py` | Database schema |
| `views.py` | Request handlers and API |
| `traefik_service.py` | Traefik integration logic |
| `urls.py` | URL routing |
| `admin.py` | Admin interface customization |
| `style.css` | UI styling and theme |
| `dashboard.js` | Frontend interactivity |
| `base.html` | Template layout |
| `index.html` | Dashboard page |

## Development Workflow

1. **Setup**: Run `start.sh` or `docker-compose up`
2. **Sync**: Run `python manage.py sync_services`
3. **Develop**: Edit code in your IDE
4. **Test**: View changes at http://localhost:8000
5. **Deploy**: Build Docker image and deploy

## Production Considerations

- Use PostgreSQL instead of SQLite
- Set `DEBUG=False`
- Configure `SECRET_KEY` securely
- Use HTTPS with Traefik
- Enable Traefik API authentication
- Set up periodic service sync (cron/systemd)
- Use proper logging
- Monitor application performance

---

For more details, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).
