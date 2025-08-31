# Microbiome Analysis Flask Web Application - Setup Instructions

## Quick Setup

This application has been successfully created with all the features you requested:

### ✅ Completed Features

1. **Google OAuth 2.0 Authentication** - Secure login system
2. **User Management** - Individual user accounts with isolated data
3. **Dataset Management** - Create, view, edit, delete datasets
4. **File Upload** - Support for CSV, TSV, XLSX, JSON files (up to 100MB)
5. **Background Processing** - Celery for async file processing
6. **Detailed Logging** - User activity tracking with individual log files
7. **Rate Limiting** - Built-in protection against abuse
8. **Responsive UI** - Bootstrap-based interface
9. **PythonAnywhere Ready** - Deployment-ready configuration

### 🚀 Quick Start

1. **Install Dependencies** (already done):
   ```bash
   # The virtual environment is already configured with all required packages
   ```

2. **Configure Google OAuth**:
   - Edit `.env` file with your Google OAuth credentials:
   ```
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

3. **Initialize Database**:
   ```bash
   .venv\Scripts\python.exe -c "from app import create_app; from extensions import db; app=create_app(); app.app_context().push(); db.create_all()"
   ```

4. **Start the Application**:
   ```bash
   .venv\Scripts\python.exe app.py
   ```

### 🔧 Production Setup (PythonAnywhere)

1. **Upload files** to your PythonAnywhere account
2. **Install dependencies** in a virtual environment
3. **Update .env** for production settings
4. **Configure WSGI** using the provided `wsgi.py` file
5. **Set up database** with PostgreSQL/MySQL

### 📁 Project Structure

```
├── app.py                 # Main application entry point
├── config.py             # Configuration settings
├── extensions.py         # Flask extensions initialization
├── models.py             # Database models (User, Dataset, AnalysisJob, UserLog)
├── celery_worker.py      # Celery worker configuration
├── wsgi.py              # WSGI configuration for production
├── 
├── auth/                # Authentication module
│   ├── routes.py        # Google OAuth implementation
│   └── __init__.py
├── 
├── datasets/            # Dataset management
│   ├── routes.py        # CRUD operations for datasets
│   └── __init__.py
├── 
├── tasks/               # Background tasks
│   ├── analysis_tasks.py # File processing and analysis
│   └── __init__.py
├── 
├── utils/               # Utility modules
│   ├── logging_config.py # Detailed user logging
│   ├── file_utils.py    # File handling utilities
│   └── __init__.py
├── 
├── templates/           # Jinja2 HTML templates
│   ├── base.html        # Base template with Bootstrap
│   ├── auth/            # Authentication templates
│   └── datasets/        # Dataset management templates
├── 
├── uploads/             # User uploaded files (auto-created)
├── logs/                # Application and user logs (auto-created)
├── 
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
├── test_setup.py       # Setup verification script
├── setup_dev.bat       # Windows setup script
└── README.md           # Detailed documentation
```

### 🔐 Security Features

- **Encapsulated Sessions**: User data is completely isolated
- **CSRF Protection**: Built-in with Flask-WTF
- **Rate Limiting**: API endpoint protection
- **File Validation**: Secure file upload handling
- **Input Sanitization**: All user inputs are validated
- **Security Headers**: HTTPS and XSS protection

### 📝 User Activity Logging

Every user action is logged in two places:
1. **Database**: `user_logs` table with structured data
2. **Individual Files**: `logs/users/user_{id}.log` with detailed logs

Logged actions include:
- Login/logout events
- Dataset creation/modification/deletion
- File uploads/downloads
- Profile changes
- All API interactions

### 🎯 What You Can Do Next

The application is ready for microbiome analysis features. You can now:

1. **Add Analysis Algorithms**: Extend `tasks/analysis_tasks.py`
2. **Create Visualization Tools**: Add plotting capabilities
3. **Implement Data Processing**: Add pandas/numpy analysis pipelines
4. **Add Export Features**: CSV/Excel/PDF report generation
5. **Extend API**: Add RESTful endpoints for external tools

### 🧪 Testing

Run the setup test anytime:
```bash
.venv\Scripts\python.exe test_setup.py
```

This will verify all components are working correctly.

### 📞 Support

The application is fully functional and secure. All core features requested have been implemented:

- ✅ Google OAuth login
- ✅ User dashboard with dataset list
- ✅ Dataset CRUD operations
- ✅ File upload and processing
- ✅ Celery background tasks
- ✅ Detailed user logging
- ✅ PythonAnywhere deployment ready
- ✅ Secure session management

You can now start adding your specific microbiome analysis features on top of this solid foundation!
