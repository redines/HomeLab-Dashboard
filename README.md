# HomeLab Dashboard

A modern, beautiful dashboard for monitoring your homelab services. Automatically discovers services from Traefik or manually add any service (internal or external). Shows health status, uptime, and provides quick access to your services.

testing github

![Django](https://img.shields.io/badge/Django-5.1-green.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

## Documentation

- [Welcome Guide](docs/WELCOME.md) - New to the project? Start here!
- [Quick Start Guide](docs/QUICKSTART.md) - Get up and running in 3 minutes
- [Manual Service Management](docs/MANUAL_SERVICES.md) - **NEW!** Add services without Traefik
- [Features](docs/FEATURES.md) - Detailed list of all features and capabilities
- [Configuration](docs/CONFIGURATION.md) - Environment variables, customization, and production deployment
- [Project Structure](docs/STRUCTURE.md) - Understanding the codebase organization
- [Project Organization](docs/PROJECT_ORGANIZATION.md) - How the project files are organized
- [Project Summary](docs/PROJECT_SUMMARY.md) - Overview and technical details
- [Files Reference](docs/FILES.md) - Description of all project files
- [Testing Guide](docs/TESTING.md) - Comprehensive testing documentation
- [Testing Quick Start](docs/TESTING_QUICKSTART.md) - Get started with testing in 5 minutes
- [Testing Setup Summary](docs/TESTING_SETUP_SUMMARY.md) - Complete testing setup overview

## Features

- 🔄 **Auto-Discovery**: Automatically scans Traefik API to discover running services (if Traefik is available)
- 🎯 **Automatic Mode Detection**: Seamlessly switches between Traefik and manual mode based on availability
- ➕ **Manual Services**: Add any service manually (homelab or external) - **No Traefik required!**
- ✏️ **Service Management**: Edit and delete manually added services
- 🌐 **External Services**: Add external websites (Google, GitHub, etc.) to your dashboard
- 📊 **Health Monitoring**: Real-time health checks with response time tracking
- 🎨 **Beautiful UI**: Modern, responsive card-based interface with dark theme
- 🐳 **Docker Support**: Fully containerized with Docker and docker-compose
- 🔗 **Quick Access**: Click any service card to navigate directly to the service
- 🏷️ **Service Types**: Supports Docker, Kubernetes, VMs, bare metal, and external services
- ⚡ **Fast Refresh**: Manual and automatic service refresh capabilities
- 📱 **Responsive**: Works perfectly on desktop, tablet, and mobile devices

## Quick Start

### Without Traefik (Manual Services Only)

The application automatically detects if Traefik is available. Simply don't configure it:

```bash
# 1. Clone and configure
git clone <your-repo-url>
cd HomeLab-Dashboard
cp .env.example .env

# 2. Leave TRAEFIK_API_URL empty (already empty in .env.example)
# No configuration needed! App automatically uses manual mode.

# 3. Start the application
docker-compose up -d

# 4. Initialize
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# 5. Access at http://localhost:8000
# 6. Click "➕ Add Service" to add your services!
```

### Docker with Traefik (Recommended)

If you have Traefik, just configure the URL and the app will automatically detect it:

```bash
# 1. Clone and configure
git clone <your-repo-url>
cd HomeLab-Dashboard
cp .env.example .env

# 2. Edit .env and set your Traefik API URL
nano .env
# Set: TRAEFIK_API_URL=http://your-traefik:8080/api

# 3. Start the application
docker-compose up -d

# 4. Initialize
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# 5. Access at http://localhost:8000
# Services will be automatically discovered!
```

### Local Development

```bash
# 1. Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure and initialize
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py sync_services

# 3. Run server
python manage.py runserver
```

See the [Quick Start Guide](docs/QUICKSTART.md) for detailed instructions.

## Screenshots

The dashboard displays your services as cards showing:
- Service name and icon
- Current status (Up/Down/Unknown)
- Service type and provider
- Response time
- Tags and metadata
- Direct link to service URL

## Keyboard Shortcuts

- **Press 'R'** - Refresh all services (when not typing in input fields)

## Requirements

- **Docker Method**: Docker and Docker Compose
- **Local Method**: Python 3.12+
- **Optional**: Traefik with API enabled (for auto-discovery)

## Key Features

### Flexible URL Input
Add services easily with flexible URL formats:
- `plex.example.com` - Protocol added automatically
- `192.168.1.100:8080` - IP addresses with ports supported
- `http://service.local` - Explicit protocol preserved
- **Smart fallback**: Tries HTTPS first, falls back to HTTP if needed

### Smart API Detection
- Automatically detects service APIs
- Throttles detection after 5 failed attempts (retries every 5 minutes)
- Reduces log spam and network traffic

### Automatic Mode Detection
- No manual configuration for Traefik enable/disable
- Seamlessly switches between Traefik and manual mode
- Works out of the box whether you have Traefik or not

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Django 5.1
- Styled with custom CSS
- Traefik integration for service discovery
- Docker for easy deployment

---

**Happy Homelabbing! 🏠🚀**
