# Microbiome Analysis Platform

A comprehensive Flask web application designed for scientific investigators to analyze microbiome data. The platform provides advanced statistical analysis tools, data visualization, and dataset management capabilities.

## Features

- **Google OAuth Authentication**: Secure login using Google accounts
- **Dataset Management**: Organize and manage microbiome datasets
- **User Dashboard**: View and manage your datasets with an intuitive interface
- **Session Management**: Isolated user sessions with Redis backend
- **Background Processing**: Celery integration for long-running analyses
- **Responsive Design**: Modern, mobile-friendly interface

## Prerequisites

- Python 3.8+
- Redis server (for sessions and Celery)
- Google Cloud Console project (for OAuth)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd MVA5
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.template .env
   ```
   
   Edit `.env` and configure the following:
   - `SECRET_KEY`: Generate a secure secret key
   - `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
   - `REDIS_URL`: Redis connection URL (default: redis://localhost:6379/0)

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client IDs
5. Configure the OAuth consent screen
6. Add authorized redirect URI: `http://127.0.0.1:5005/auth/login/authorized`
7. Copy the Client ID and Client Secret to your `.env` file

## Redis Setup

### Local Redis Installation

**Windows**:
- Download Redis from [GitHub releases](https://github.com/tporadowski/redis/releases)
- Install and start Redis service

**macOS**:
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

### Cloud Redis (Alternative)

You can use cloud Redis services like:
- Redis Cloud
- AWS ElastiCache
- Google Cloud Memorystore

Update the `REDIS_URL` in your `.env` file accordingly.

## Running the Application

1. **Start Redis** (if running locally):
   ```bash
   redis-server
   ```

2. **Start the Flask application**:
   ```bash
   python app.py
   ```

3. **Start Celery worker** (in a separate terminal):
   ```bash
   celery -A celery_app worker --loglevel=info
   ```

4. **Start Celery beat** (for periodic tasks, in another terminal):
   ```bash
   celery -A celery_app beat --loglevel=info
   ```

5. **Access the application**:
   Open your browser and go to `http://127.0.0.1:5005`

## Project Structure

```
MVA5/
├── app.py                 # Main Flask application
├── celery_app.py         # Celery configuration
├── requirements.txt      # Python dependencies
├── env.template          # Environment variables template
├── architecture/         # Project configuration and documentation
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── new_dataset.html
│   ├── dataset.html
│   └── error.html
├── static/              # Static files
│   ├── css/
│   ├── js/
│   └── images/
├── tasks/               # Celery tasks
│   ├── __init__.py
│   └── maintenance.py
└── uploads/             # File upload directory (created automatically)
```

## Usage

1. **Login**: Click "Login with Google" on the homepage
2. **Create Dataset**: After login, create a new dataset from the dashboard
3. **Upload Files**: Upload your microbiome data files to the dataset
4. **Run Analysis**: Use the analysis tools to process your data
5. **View Results**: Download or view analysis results

## Development

### Adding New Features

1. **Models**: Add new database models in `app.py`
2. **Routes**: Add new routes in `app.py` or create separate blueprints
3. **Templates**: Create new HTML templates in the `templates/` directory
4. **Tasks**: Add Celery tasks in the `tasks/` directory
5. **Static Files**: Add CSS/JS files in the `static/` directory

### Database Migrations

For development, the app creates tables automatically. For production, consider using Flask-Migrate:

```bash
pip install Flask-Migrate
```

## Deployment

### PythonAnywhere Deployment

1. Upload your code to PythonAnywhere
2. Create a web app with manual configuration
3. Install dependencies in a virtual environment
4. Configure the WSGI file to point to your Flask app
5. Set up environment variables in the web app settings
6. Use PythonAnywhere's Redis service or an external Redis provider

### Environment Variables for Production

Make sure to set secure values for:
- `SECRET_KEY`: Use a strong, randomly generated key
- `WTF_CSRF_SECRET_KEY`: Use a different strong key
- `SESSION_COOKIE_SECURE=True`: For HTTPS deployments
- `FLASK_ENV=production`
- `FLASK_DEBUG=False`

## Security Considerations

- Always use HTTPS in production
- Set secure session cookie flags
- Use strong secret keys
- Regularly update dependencies
- Implement proper input validation
- Use environment variables for sensitive data

## Support

For issues or questions, please check the project documentation in the `architecture/` directory.

## License

This project is developed for scientific research purposes.
