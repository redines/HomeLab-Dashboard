# HomeLab Dashboard

A modern, beautiful dashboard for monitoring your homelab services. Automatically discovers services from Traefik, shows health status, uptime, and provides quick access to your services.

![Django](https://img.shields.io/badge/Django-5.1-green.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

## Documentation

- [Welcome Guide](docs/WELCOME.md) - New to the project? Start here!
- [Quick Start Guide](docs/QUICKSTART.md) - Get up and running in 3 minutes
- [Features](docs/FEATURES.md) - Detailed list of all features and capabilities
- [Configuration](docs/CONFIGURATION.md) - Environment variables, customization, and production deployment
- [Project Structure](docs/STRUCTURE.md) - Understanding the codebase organization
- [Project Summary](docs/PROJECT_SUMMARY.md) - Overview and technical details
- [Files Reference](docs/FILES.md) - Description of all project files

## Features

- 🔄 **Auto-Discovery**: Automatically scans Traefik API to discover running services
- 📊 **Health Monitoring**: Real-time health checks with response time tracking
- 🎨 **Beautiful UI**: Modern, responsive card-based interface with dark theme
- 🐳 **Docker Support**: Fully containerized with Docker and docker-compose
- 🔗 **Quick Access**: Click any service card to navigate directly to the service
- 🏷️ **Service Types**: Supports Docker, Kubernetes, VMs, and bare metal deployments
- ⚡ **Fast Refresh**: Manual and automatic service refresh capabilities
- 📱 **Responsive**: Works perfectly on desktop, tablet, and mobile devices

## Quick Start

### Docker (Recommended)

```bash
# 1. Clone and configure
git clone <your-repo-url>
cd HomeLab-Dashboard
cp .env.example .env

# 2. Edit docker-compose.yml with your Traefik API URL

# 3. Start the application
docker-compose up -d

# 4. Initialize
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py sync_services

# 5. Access at http://localhost:8000
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

## Requirements

- **Docker Method**: Docker and Docker Compose
- **Local Method**: Python 3.12+
- **Required**: Traefik with API enabled

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
