@echo off
REM Development setup script for Windows

echo Setting up Microbiome Analysis Web Application for development...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create environment file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit .env file with your configuration before running the app.
)

REM Create necessary directories
echo Creating directories...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs

REM Initialize database
echo Initializing database...
flask db init 2>nul || echo Database already initialized
flask db migrate -m "Initial migration" 2>nul || echo Migration already exists
flask db upgrade

echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your Google OAuth credentials
echo 2. Start Redis server in a separate command prompt
echo 3. Start Celery worker in a separate command prompt: celery -A celery_worker.celery_app worker --loglevel=info
echo 4. Run the application: python app.py

pause
