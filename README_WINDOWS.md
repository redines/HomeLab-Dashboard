# HomeLab Dashboard - Windows Setup Guide

This guide will help you run the HomeLab Dashboard on Windows.

## Prerequisites

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
  - During installation, make sure to check "Add Python to PATH"
- **Node.js 18.x or higher** - [Download Node.js](https://nodejs.org/)
- **Git** (optional) - [Download Git](https://git-scm.com/download/win)

## Quick Start

### Option 1: Using Batch File (Easiest)

Simply double-click `start.bat` in the project root, or run from Command Prompt:

```cmd
start.bat
```

### Option 2: Using PowerShell Script

Open PowerShell in the project root and run:

```powershell
.\scripts\start.ps1
```

If you get an execution policy error, run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try running the script again.

### Option 3: Manual Setup

1. **Create a virtual environment:**
   ```cmd
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   ```cmd
   venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies:**
   ```cmd
   npm install
   ```

5. **Run database migrations:**
   ```cmd
   python manage.py migrate
   ```

6. **Create a superuser:**
   ```cmd
   python manage.py createsuperuser
   ```

7. **Build Tailwind CSS:**
   ```cmd
   npm run build:css
   ```

8. **Start the development server:**
   ```cmd
   npm run dev
   ```

## Running Tests

### Using PowerShell Script

```powershell
.\scripts\run_tests.ps1
```

Or run specific test types:

```powershell
# Backend tests only
.\scripts\run_tests.ps1 backend

# Frontend tests only
.\scripts\run_tests.ps1 frontend

# Integration tests only
.\scripts\run_tests.ps1 integration

# Unit tests only
.\scripts\run_tests.ps1 unit

# All tests without coverage
.\scripts\run_tests.ps1 all false
```

### Manual Testing

```cmd
# Activate virtual environment first
venv\Scripts\activate

# Run backend tests
python -m pytest tests/

# Run frontend tests
npm test

# Run with coverage
python -m pytest tests/ --cov=dashboard --cov-report=html
npm test -- --coverage
```

## Accessing the Dashboard

Once the server is running:

- **Dashboard:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin

## Common Issues

### PowerShell Execution Policy Error

If you get "cannot be loaded because running scripts is disabled", run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Not Found

Make sure Python is in your PATH. You can test by running:

```cmd
python --version
```

If it's not found, reinstall Python and check "Add Python to PATH" during installation.

### npm Not Found

Make sure Node.js is installed and in your PATH:

```cmd
node --version
npm --version
```

### Port 8000 Already in Use

If port 8000 is already taken, you can run the server on a different port:

```cmd
python manage.py runserver 8080
```

Then access the dashboard at http://localhost:8080

## Project Structure

```
homelab_dashboard/
├── start.bat                 # Quick start batch file
├── scripts/
│   ├── start.ps1            # PowerShell startup script
│   ├── start.sh             # Linux/Mac startup script
│   ├── run_tests.ps1        # PowerShell test runner
│   └── run_tests.sh         # Linux/Mac test runner
├── dashboard/               # Main Django app
├── static/                  # Static files (CSS, JS)
├── templates/               # HTML templates
└── requirements.txt         # Python dependencies
```

## Environment Variables

Create a `.env` file in the project root for custom configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
FIELD_ENCRYPTION_KEY=your-encryption-key-here
```

To generate an encryption key:

```cmd
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Additional Commands

```cmd
# Activate virtual environment
venv\Scripts\activate

# Deactivate virtual environment
deactivate

# Run management commands
python manage.py <command>

# Sync services
python manage.py sync_services

# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Run shell
python manage.py shell
```

## Development

The development server will automatically reload when you make changes to Python files. For CSS changes, the Tailwind watcher will automatically rebuild the styles.

To stop the servers, press `Ctrl+C` in the terminal.

## Support

For more information, see the main [README.md](README.md) and documentation in the `docs/` folder.
