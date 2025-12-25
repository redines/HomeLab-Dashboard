#!/bin/bash

# HomeLab Dashboard - Development Startup Script

echo "🏠 Starting HomeLab Dashboard Development Server"
echo "=================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if database exists
if [ ! -f "db.sqlite3" ]; then
    echo "🗄️  Database not found. Running initial setup..."
    
    # Run migrations
    echo "   - Running migrations..."
    python manage.py migrate
    
    # Create superuser prompt
    echo ""
    echo "📝 Create a superuser account for the admin panel:"
    python manage.py createsuperuser
    
    echo ""
    echo "✅ Initial setup complete!"
else
    echo "🗄️  Database found. Running migrations..."
    python manage.py migrate
fi

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear > /dev/null 2>&1 || true

echo ""
echo "=================================================="
echo "✨ HomeLab Dashboard is ready!"
echo ""
echo "📍 Dashboard: http://localhost:8000"
echo "🔐 Admin Panel: http://localhost:8000/admin"
echo ""
echo "💡 Useful commands:"
echo "   - Sync services: python manage.py sync_services"
echo "   - Create superuser: python manage.py createsuperuser"
echo "   - Stop server: Press Ctrl+C"
echo ""
echo "🚀 Starting development server..."
echo "=================================================="
echo ""

# Start the development server
python manage.py runserver
