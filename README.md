# Microbiome Analysis Platform

A comprehensive Flask web application for microbiome data analysis with secure user management, background processing, and advanced analytical tools.

![Platform](https://img.shields.io/badge/Platform-Flask-green.svg)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Features

### Core Functionality
- **User Authentication**: Google OAuth 2.0 integration for secure login
- **Dataset Management**: Per-user dataset creation, upload, and management
- **Background Processing**: Celery-powered async tasks with Redis backend
- **Advanced Analytics**: Statistical analysis tools for microbiome data
- **Comprehensive Logging**: Detailed per-user activity logs and audit trails

### Technical Highlights
- **Flask App Factory**: Scalable application architecture
- **SQLAlchemy ORM**: Database abstraction with migration support
- **Bootstrap 5**: Modern, responsive UI design
- **Security First**: CSRF protection, secure sessions, rate limiting
- **Production Ready**: Gunicorn configuration and PythonAnywhere deployment support

## 🛠️ Technology Stack

- **Backend**: Flask 3.x, SQLAlchemy, Celery
- **Frontend**: Bootstrap 5, Font Awesome, Custom CSS
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Queue**: Redis + Celery
- **Authentication**: Google OAuth 2.0 via Authlib
- **Analytics**: pandas, scipy, scikit-learn, matplotlib

## 📋 Prerequisites

- Python 3.9+
- Redis server
- Google OAuth credentials
- Modern web browser

## 🔧 Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd microbiome-analysis-platform
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment setup
Create a `.env` file:
```env
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:5002/auth/callback
OAUTHLIB_INSECURE_TRANSPORT=1
DATABASE_URL=sqlite:///app.db
REDIS_URL=redis://localhost:6379/0
PORT=5002
DEBUG=1
```

### 5. Initialize database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🚀 Quick Start

### 1. Start Redis server
```bash
redis-server
```

### 2. Start Celery worker
```bash
celery -A celery_worker.celery_app worker --loglevel=info
```

### 3. Run the application
```bash
python app.py
```

Visit `http://127.0.0.1:5002` in your browser.

## 📁 Project Structure

```
├── app.py                  # Application entry point
├── config.py              # Configuration classes
├── extensions.py          # Flask extensions initialization
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
│
├── auth/                  # Authentication blueprint
│   ├── __init__.py
│   └── routes.py         # OAuth routes and user management
│
├── datasets/             # Dataset management blueprint
│   ├── __init__.py
│   └── routes.py        # Dataset CRUD and upload handling
│
├── tasks/               # Celery background tasks
│   └── analysis_tasks.py # Data processing and analysis
│
├── utils/               # Utility modules
│   ├── file_utils.py   # File handling utilities
│   └── logging_config.py # Logging configuration
│
├── templates/           # Jinja2 HTML templates
│   ├── base.html       # Base template
│   ├── auth/           # Authentication templates
│   └── datasets/       # Dataset management templates
│
├── static/             # Static files (CSS, JS, images)
├── uploads/            # User uploaded files (gitignored)
├── logs/              # Application logs (gitignored)
└── migrations/        # Database migrations (gitignored)
```

## 🔐 Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://127.0.0.1:5002/auth/callback`
6. Copy Client ID and Secret to your `.env` file

## 🧪 Testing

Run the test suite:
```bash
python test_setup.py
```

## 📊 Features in Detail

### Dataset Management
- **Upload**: Support for various file formats (CSV, Excel, FASTA)
- **Validation**: Automatic file validation and metadata extraction
- **Processing**: Background analysis with progress tracking
- **Sharing**: Secure per-user data isolation

### Analysis Tools
- **Diversity Metrics**: Alpha and beta diversity calculations
- **Statistical Analysis**: Differential abundance testing
- **Visualization**: Interactive plots and charts
- **Export**: Results in multiple formats

### Security
- **Authentication**: Google OAuth 2.0 integration
- **Authorization**: Role-based access control
- **Logging**: Comprehensive audit trails
- **Rate Limiting**: Protection against abuse

## 🚀 Deployment

### PythonAnywhere
1. Upload code to PythonAnywhere
2. Install dependencies in virtual environment
3. Configure WSGI file to use `wsgi.py`
4. Set environment variables in web app settings
5. Start Celery worker as background task

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions

## 🔄 Changelog

### v1.0.0 (Current)
- Initial release
- Google OAuth authentication
- Dataset upload and management
- Background processing with Celery
- Responsive Bootstrap UI
- Comprehensive logging system

---

Built with ❤️ for the microbiome research community.
