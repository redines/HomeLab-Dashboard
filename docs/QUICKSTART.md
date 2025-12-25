# Quick Start Guide

Get your HomeLab Dashboard up and running in 3 minutes!

## Prerequisites

- Docker and Docker Compose installed (for Docker method)
- Python 3.12+ (for local development method)
- **Optional**: Traefik running with API enabled (for auto-discovery)

**Note**: Traefik is optional! The dashboard works perfectly without it using manual service management.

## Option 1: Docker (Recommended)

**Fastest way to get started!**

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd HomeLab-Dashboard
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Update docker-compose.yml

Edit the `TRAEFIK_API_URL` to point to your Traefik instance:
```yaml
environment:
  - TRAEFIK_API_URL=http://your-traefik-host:8080/api
```

### 4. Build and run

```bash
docker-compose up -d
```

### 5. Initialize the database

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 6. Sync services from Traefik

```bash
docker-compose exec web python manage.py sync_services
```

### 7. Access the dashboard

Open your browser and navigate to: `http://localhost:8000`

---

## Option 2: Local Development

**Best for development and customization**

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd HomeLab-Dashboard
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your Traefik API settings
```

### 5. Run migrations

```bash
chmod +x manage.py
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Sync services from Traefik

```bash
python manage.py sync_services
```

### 8. Run the development server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to see your dashboard!

---

## First Time Setup Checklist

- [ ] Traefik is running with API enabled
- [ ] Configure TRAEFIK_API_URL in .env or docker-compose.yml
- [ ] Run database migrations
- [ ] Create superuser account
- [ ] Sync services from Traefik
- [ ] Access dashboard at http://localhost:8000

## Common Commands

### Docker
```bash
# View logs
docker-compose logs -f web

# Restart container
docker-compose restart web

# Stop everything
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Local Development
```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
python manage.py runserver

# Sync services
python manage.py sync_services

# Access Django shell
python manage.py shell

# Create migrations
python manage.py makemigrations
```

## Troubleshooting

### No services showing up?

1. Check Traefik API is accessible:
   ```bash
   curl http://your-traefik-host:8080/api/http/routers
   ```

2. Verify TRAEFIK_API_URL in your configuration

3. Run sync manually:
   ```bash
   python manage.py sync_services
   # or in Docker:
   docker-compose exec web python manage.py sync_services
   ```

4. Check logs for errors:
   ```bash
   docker-compose logs web
   ```

### Can't connect to Traefik?

- Ensure Docker containers are on the same network
- Check firewall rules
- Verify Traefik API is enabled (see traefik-example.yml)

### Database errors?

```bash
# Reset database (WARNING: deletes all data)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Next Steps

1. **Customize Services**
   - Visit http://localhost:8000/admin
   - Add descriptions, icons, and tags to your services
   - Set service types (Docker, Kubernetes, etc.)

2. **Configure Auto-Refresh**
   - Edit static/js/dashboard.js
   - Uncomment the auto-refresh line
   - Adjust refresh interval as needed

3. **Production Deployment**
   - Set DEBUG=False
   - Configure strong SECRET_KEY
   - Use PostgreSQL instead of SQLite
   - Enable HTTPS with Traefik
   - Set up periodic sync with cron

4. **Explore Features**
   - Health checks for all services
   - Historical health tracking
   - API endpoints for automation
   - Keyboard shortcuts (press 'R' to refresh)

## Getting Help

- Check the full README.md for detailed documentation
- Review traefik-example.yml for Traefik setup
- Check Django logs for error messages
- Ensure all environment variables are set correctly

---

Happy homelabbing! 🏠🚀
