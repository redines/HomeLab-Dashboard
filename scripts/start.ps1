# HomeLab Dashboard - Development Startup Script for Windows

# Change to project root directory (parent of scripts/)
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$SCRIPT_DIR\.."

Write-Host "🏠 Starting HomeLab Dashboard Development Server" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install/upgrade dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Check if database exists
if (-not (Test-Path "db.sqlite3")) {
    Write-Host "🗄️  Database not found. Running initial setup..." -ForegroundColor Yellow
    
    # Run migrations
    Write-Host "   - Running migrations..." -ForegroundColor Gray
    python manage.py migrate
    
    # Create superuser prompt
    Write-Host ""
    Write-Host "📝 Create a superuser account for the admin panel:" -ForegroundColor Green
    python manage.py createsuperuser
    
    Write-Host ""
    Write-Host "✅ Initial setup complete!" -ForegroundColor Green
} else {
    Write-Host "🗄️  Database found. Running migrations..." -ForegroundColor Yellow
    python manage.py migrate
}

# Install node dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing Node dependencies..." -ForegroundColor Yellow
    npm install
}

# Build Tailwind CSS initially
Write-Host "🎨 Building Tailwind CSS..." -ForegroundColor Yellow
npm run build:css 2>&1 | Out-Null

# Collect static files
Write-Host "📦 Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --clear 2>&1 | Out-Null

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "✨ HomeLab Dashboard is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Dashboard: http://localhost:8000" -ForegroundColor White
Write-Host "🔐 Admin Panel: http://localhost:8000/admin" -ForegroundColor White
Write-Host ""
Write-Host "💡 Useful commands:" -ForegroundColor Cyan
Write-Host "   - Sync services: python manage.py sync_services" -ForegroundColor Gray
Write-Host "   - Create superuser: python manage.py createsuperuser" -ForegroundColor Gray
Write-Host "   - Stop servers: Press Ctrl+C" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Starting development server with Tailwind watch..." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Start both the Tailwind watcher and development server
npm run dev
