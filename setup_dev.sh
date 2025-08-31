#!/bin/bash
# Development setup script

echo "Setting up Microbiome Analysis Web Application for development..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your configuration before running the app."
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads logs

# Initialize database
echo "Initializing database..."
flask db init || echo "Database already initialized"
flask db migrate -m "Initial migration" || echo "Migration already exists"
flask db upgrade

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Google OAuth credentials"
echo "2. Start Redis server: redis-server"
echo "3. Start Celery worker: celery -A celery_worker.celery_app worker --loglevel=info"
echo "4. Run the application: python app.py"
