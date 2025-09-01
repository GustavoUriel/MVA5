"""
Microbiome Analysis Flask Web Application
Main application entry point
"""

import os
import uuid
import time
from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from datetime import datetime
# import redis  # Commented out since we're using filesystem sessions
from celery import Celery
from dotenv import load_dotenv
from logging_config import setup_logging, ErrorLogger, log_user_action, log_performance, PerformanceTracker

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)



# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///microbiome_analysis.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'microbiome:'
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

# Google OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID', 'dummy-client-id')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET', 'dummy-client-secret')
app.config['GOOGLE_REDIRECT_URI'] = os.environ.get('GOOGLE_REDIRECT_URI', 'http://127.0.0.1:5005/auth/login/authorized')

# Celery Configuration
app.config['CELERY_BROKER_URL'] = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
Session(app)
oauth = OAuth(app)

# Configure Google OAuth
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Initialize Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    profile_pic = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship with datasets
    datasets = db.relationship('Dataset', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Dataset metadata
    status = db.Column(db.String(50), default='draft')  # draft, processing, ready, error
    file_count = db.Column(db.Integer, default=0)
    total_size = db.Column(db.BigInteger, default=0)  # in bytes
    
    def __repr__(self):
        return f'<Dataset {self.name}>'

# Routes
@app.route('/')
def index():
    """Welcome page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing datasets"""
    datasets = Dataset.query.filter_by(user_id=current_user.id).order_by(Dataset.updated_at.desc()).all()
    return render_template('dashboard.html', datasets=datasets, user=current_user)

@app.route('/dataset/new', methods=['GET', 'POST'])
@login_required
def new_dataset():
    """Create a new dataset"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Dataset name is required.', 'error')
            return render_template('new_dataset.html')
        
        # Check if dataset name already exists for this user
        existing = Dataset.query.filter_by(user_id=current_user.id, name=name).first()
        if existing:
            flash('A dataset with this name already exists.', 'error')
            return render_template('new_dataset.html')
        
        # Create new dataset
        dataset = Dataset(
            name=name,
            description=description,
            user_id=current_user.id
        )
        
        try:
            with PerformanceTracker("dataset_creation", f"Dataset: {name}"):
                db.session.add(dataset)
                db.session.commit()
                
            log_user_action("dataset_created", f"Dataset: {name}", success=True)
            flash(f'Dataset "{name}" created successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            ErrorLogger.log_exception(
                e,
                context="Creating new dataset",
                user_action=f"User trying to create dataset '{name}'",
                extra_data={
                    'dataset_name': name,
                    'dataset_description': description,
                    'user_id': current_user.id if current_user.is_authenticated else None
                }
            )
            log_user_action("dataset_creation_failed", f"Dataset: {name}", success=False)
            flash('Error creating dataset. Please try again.', 'error')
            app.logger.error(f'Error creating dataset: {e}')
    
    return render_template('new_dataset.html')

@app.route('/dataset/<int:dataset_id>')
@login_required
def view_dataset(dataset_id):
    """View a specific dataset"""
    dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first_or_404()
    return render_template('dataset.html', dataset=dataset)

# Authentication routes
@app.route('/auth/login')
def login():
    """Initiate Google OAuth login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Check if OAuth is properly configured
    if (app.config['GOOGLE_CLIENT_ID'] == 'dummy-client-id' or 
        app.config['GOOGLE_CLIENT_SECRET'] == 'dummy-client-secret'):
        ErrorLogger.log_warning(
            "OAuth not configured - using dummy credentials",
            context="Google OAuth login attempt",
            user_action="User trying to log in with Google",
            extra_data={
                'oauth_provider': 'google',
                'client_id_configured': app.config['GOOGLE_CLIENT_ID'] != 'dummy-client-id',
                'client_secret_configured': app.config['GOOGLE_CLIENT_SECRET'] != 'dummy-client-secret'
            }
        )
        log_user_action("oauth_config_error", "OAuth not properly configured", success=False)
        flash('Google OAuth is not configured. Please set up GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your environment variables.', 'error')
        return redirect(url_for('index'))
    
    try:
        with PerformanceTracker("oauth_initiate", "Google OAuth redirect"):
            redirect_uri = url_for('auth_callback', _external=True)
            result = google.authorize_redirect(redirect_uri)
        log_user_action("oauth_initiate", "Google OAuth redirect initiated", success=True)
        return result
    except Exception as e:
        ErrorLogger.log_exception(
            e,
            context="Initiating Google OAuth login",
            user_action="User trying to log in with Google",
            extra_data={
                'oauth_provider': 'google',
                'redirect_uri': request.url,
                'error_type': 'oauth_initiation_error'
            }
        )
        log_user_action("oauth_initiate_failed", "Google OAuth redirect failed", success=False)
        app.logger.error(f'OAuth configuration error: {e}')
        flash('Authentication service is not available. Please try again later.', 'error')
        return redirect(url_for('index'))

@app.route('/auth/login/authorized')
def auth_callback():
    """Handle Google OAuth callback"""
    # Check if OAuth is properly configured first
    if (app.config['GOOGLE_CLIENT_ID'] == 'dummy-client-id' or 
        app.config['GOOGLE_CLIENT_SECRET'] == 'dummy-client-secret'):
        ErrorLogger.log_warning(
            "OAuth callback with dummy credentials",
            context="Google OAuth callback processing",
            user_action="User completing OAuth login",
            extra_data={
                'oauth_provider': 'google',
                'callback_url': request.url,
                'error_type': 'oauth_not_configured'
            }
        )
        log_user_action("oauth_callback_error", "OAuth not configured for callback", success=False)
        flash('Google OAuth is not configured. Please set up OAuth credentials.', 'error')
        return redirect(url_for('index'))
    
    try:
        with PerformanceTracker("oauth_callback", "Google OAuth token exchange"):
            # Get the authorization code from the request
            code = request.args.get('code')
            if not code:
                raise ValueError("No authorization code received")
            
            # Exchange code for access token manually
            token_url = 'https://oauth2.googleapis.com/token'
            token_data = {
                'client_id': app.config['GOOGLE_CLIENT_ID'],
                'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': url_for('auth_callback', _external=True)
            }
            
            import requests
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_info = token_response.json()
            
            # Get user info using the access token
            userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
            headers = {'Authorization': f"Bearer {token_info['access_token']}"}
            userinfo_response = requests.get(userinfo_url, headers=headers)
            userinfo_response.raise_for_status()
            user_info = userinfo_response.json()
        
        if user_info:
            with PerformanceTracker("user_login_process", f"User: {user_info.get('email')}"):
                # Check if user exists
                user = User.query.filter_by(google_id=user_info['id']).first()
                
                if not user:
                    # Create new user
                    user = User(
                        email=user_info['email'],
                        name=user_info['name'],
                        google_id=user_info['id'],
                        profile_pic=user_info.get('picture'),
                        last_login=datetime.utcnow()
                    )
                    db.session.add(user)
                    log_user_action("user_created", f"New user: {user_info['email']}", success=True)
                else:
                    # Update existing user
                    user.last_login = datetime.utcnow()
                    user.name = user_info['name']
                    user.profile_pic = user_info.get('picture')
                
                db.session.commit()
                login_user(user, remember=True)
                
            log_user_action("user_login", f"Successful login: {user.email}", success=True)
            flash(f'Welcome, {user.name}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            ErrorLogger.log_exception(
                ValueError("No user info received from Google API"),
                context="OAuth callback processing",
                user_action="User completing OAuth login",
                extra_data={'token_info': str(token_info) if 'token_info' in locals() else None}
            )
            log_user_action("oauth_callback_failed", "No user info from API", success=False)
        
    except Exception as e:
        ErrorLogger.log_exception(
            e,
            context="Processing Google OAuth callback",
            user_action="User completing OAuth login",
            extra_data={
                'oauth_provider': 'google',
                'callback_url': request.url,
                'user_agent': request.headers.get('User-Agent'),
                'error_type': 'oauth_callback_error'
            }
        )
        log_user_action("oauth_callback_failed", f"OAuth callback error: {str(e)}", success=False)
        app.logger.error(f'OAuth error: {e}')
        flash('Authentication failed. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/auth/logout')
@login_required
def logout():
    """Logout user"""
    try:
        user_email = current_user.email if current_user.is_authenticated else 'unknown'
        logout_user()
        log_user_action("user_logout", f"User logged out: {user_email}", success=True)
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('index'))
    except Exception as e:
        ErrorLogger.log_exception(
            e,
            context="User logout process",
            user_action="User trying to logout",
            extra_data={'user_id': current_user.id if current_user.is_authenticated else None}
        )
        log_user_action("logout_failed", "Logout process failed", success=False)
        flash('Logout encountered an error, but you have been logged out.', 'warning')
        return redirect(url_for('index'))

# API routes
@app.route('/api/datasets')
@login_required
def api_datasets():
    """API endpoint to get user's datasets"""
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': d.id,
        'name': d.name,
        'description': d.description,
        'status': d.status,
        'file_count': d.file_count,
        'created_at': d.created_at.isoformat(),
        'updated_at': d.updated_at.isoformat()
    } for d in datasets])

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    ErrorLogger.log_exception(
        error,
        context="Bad request error (400)",
        user_action=f"User accessing {request.url}",
        extra_data={
            'error_description': str(error.description) if hasattr(error, 'description') else None,
            'request_method': request.method,
            'request_data': dict(request.form) if request.form else None
        }
    )
    log_user_action("error_400", f"Bad request: {request.url}", success=False)
    return render_template('error.html', error='Bad request', code=400), 400

@app.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized access errors"""
    ErrorLogger.log_exception(
        error,
        context="Unauthorized access error (401)",
        user_action=f"User trying to access {request.url}",
        extra_data={
            'requires_login': True,
            'requested_endpoint': request.endpoint
        }
    )
    log_user_action("error_401", f"Unauthorized access: {request.url}", success=False)
    return render_template('error.html', error='Unauthorized access', code=401), 401

@app.errorhandler(403)
def forbidden(error):
    """Handle forbidden access errors"""
    ErrorLogger.log_exception(
        error,
        context="Forbidden access error (403)",
        user_action=f"User trying to access {request.url}",
        extra_data={
            'user_has_permission': False,
            'requested_endpoint': request.endpoint
        }
    )
    log_user_action("error_403", f"Forbidden access: {request.url}", success=False)
    return render_template('error.html', error='Access forbidden', code=403), 403

@app.errorhandler(404)
def not_found(error):
    """Handle page not found errors"""
    ErrorLogger.log_warning(
        f"Page not found: {request.url}",
        context="404 error - page not found",
        user_action=f"User trying to access non-existent page",
        extra_data={
            'referrer': request.referrer,
            'user_agent': request.headers.get('User-Agent')
        }
    )
    log_user_action("error_404", f"Page not found: {request.url}", success=False)
    return render_template('error.html', error='Page not found', code=404), 404

@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large errors"""
    ErrorLogger.log_exception(
        error,
        context="File upload too large (413)",
        user_action="User trying to upload file",
        extra_data={
            'max_content_length': app.config.get('MAX_CONTENT_LENGTH'),
            'content_length': request.content_length
        }
    )
    log_user_action("error_413", "File upload too large", success=False)
    return render_template('error.html', error='File too large', code=413), 413

@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle rate limit exceeded errors"""
    ErrorLogger.log_exception(
        error,
        context="Rate limit exceeded (429)",
        user_action=f"User making too many requests to {request.url}",
        extra_data={
            'rate_limit_info': str(error.description) if hasattr(error, 'description') else None
        }
    )
    log_user_action("error_429", "Rate limit exceeded", success=False)
    return render_template('error.html', error='Too many requests', code=429), 429

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    db.session.rollback()
    
    ErrorLogger.log_exception(
        error,
        context="Internal server error (500)",
        user_action=f"User accessing {request.url}",
        extra_data={
            'error_type': type(error).__name__ if error else 'Unknown',
            'database_rollback': True
        }
    )
    log_user_action("error_500", f"Internal server error: {request.url}", success=False)
    return render_template('error.html', error='Internal server error', code=500), 500

@app.errorhandler(502)
def bad_gateway(error):
    """Handle bad gateway errors"""
    ErrorLogger.log_exception(
        error,
        context="Bad gateway error (502)",
        user_action=f"User accessing {request.url}",
        extra_data={'upstream_service_error': True}
    )
    log_user_action("error_502", "Bad gateway error", success=False)
    return render_template('error.html', error='Service temporarily unavailable', code=502), 502

@app.errorhandler(503)
def service_unavailable(error):
    """Handle service unavailable errors"""
    ErrorLogger.log_exception(
        error,
        context="Service unavailable error (503)",
        user_action=f"User accessing {request.url}",
        extra_data={'service_maintenance': True}
    )
    log_user_action("error_503", "Service unavailable", success=False)
    return render_template('error.html', error='Service unavailable', code=503), 503

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    """Handle any unexpected errors"""
    db.session.rollback()
    
    ErrorLogger.log_exception(
        error,
        context="Unexpected error - Global exception handler",
        user_action=f"User accessing {request.url}",
        extra_data={
            'unexpected_error': True,
            'error_class': error.__class__.__name__,
            'database_rollback': True
        }
    )
    log_user_action("error_unexpected", f"Unexpected error: {type(error).__name__}", success=False)
    
    # Return appropriate error response based on request type
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'An unexpected error occurred',
            'code': 500,
            'request_id': getattr(request, 'request_id', 'unknown')
        }), 500
    else:
        return render_template('error.html', 
                             error='An unexpected error occurred', 
                             code=500), 500

# Set up comprehensive logging
setup_logging(app)

# Request tracking middleware
@app.before_request
def before_request():
    """Track request start time and assign request ID"""
    g.start_time = time.time()
    g.request_id = str(uuid.uuid4())[:8]
    request.request_id = g.request_id
    
    # Log request start for audit trail
    if request.endpoint not in ['static', None]:
        log_user_action(
            f"REQUEST_START",
            f"{request.method} {request.path}",
            success=True
        )

@app.after_request
def after_request(response):
    """Log request completion and performance"""
    if hasattr(g, 'start_time') and request.endpoint not in ['static', None]:
        duration = time.time() - g.start_time
        
        # Log performance
        log_performance(
            f"{request.method} {request.endpoint or request.path}",
            duration,
            f"Status: {response.status_code}"
        )
        
        # Log request completion
        log_user_action(
            f"REQUEST_END",
            f"{request.method} {request.path} - Status: {response.status_code}",
            success=response.status_code < 400,
            duration=duration
        )
    
    return response

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005, debug=True)
