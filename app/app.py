"""
Microbiome Analysis Flask Web Application
Main application entry point
"""

from flask_login import UserMixin
import os
import uuid
import time
import json
import shutil
from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify, g, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from datetime import datetime
# import redis  # Commented out since we're using filesystem sessions
from celery import Celery
from dotenv import load_dotenv
from .scripts.logging_config import setup_logging, ErrorLogger, log_user_action, log_performance, PerformanceTracker
from .scripts.smart_table import build_schema, build_table_data, save_table
from .database import db
from .modules import User, Dataset, DatasetFile
from .modules.main.main_bp import main_bp
from .modules.auth.auth_bp import auth_bp
from .modules.datasets.datasets_bp import datasets_bp
from .modules.files.files_bp import files_bp
from .modules.api.api_bp import api_bp
from .modules.editor.editor_bp import editor_bp
# Load environment variables
load_dotenv()


def create_app():
  # Initialize Flask app
  app = Flask(__name__)

  # Configuration
  app.config['SECRET_KEY'] = os.environ.get(
      'SECRET_KEY', 'dev-secret-key-change-in-production')
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
      'DATABASE_URL', 'sqlite:///microbiome_analysis.db')
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

  # Initialize SQLAlchemy with the app
  db.init_app(app)
  app.config['SESSION_TYPE'] = 'filesystem'
  app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
  app.config['SESSION_PERMANENT'] = False
  app.config['SESSION_USE_SIGNER'] = True
  app.config['SESSION_KEY_PREFIX'] = 'microbiome:'
  app.config['UPLOAD_FOLDER'] = os.path.join(
      os.getcwd(), os.environ.get('UPLOAD_FOLDER', 'uploads'))
  app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get(
      'MAX_CONTENT_LENGTH', 100 * 1024 * 1024))  # 100MB

  # Google OAuth Configuration
  app.config['GOOGLE_CLIENT_ID'] = os.environ.get(
      'GOOGLE_CLIENT_ID', 'dummy-client-id')
  app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get(
      'GOOGLE_CLIENT_SECRET', 'dummy-client-secret')
  app.config['GOOGLE_REDIRECT_URI'] = os.environ.get(
      'GOOGLE_REDIRECT_URI', 'http://127.0.0.1:5005/auth/login/authorized')

  # Celery Configuration
  app.config['CELERY_BROKER_URL'] = os.environ.get(
      'CELERY_BROKER_URL', 'redis://localhost:6379/0')
  app.config['CELERY_RESULT_BACKEND'] = os.environ.get(
      'CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

  # Initialize extensions
  login_manager = LoginManager(app)
  login_manager.login_view = 'login'
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

  # Store OAuth client on app for access from blueprints
  app.google = google

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

  # Register blueprints
  app.register_blueprint(main_bp)
  app.register_blueprint(auth_bp)
  app.register_blueprint(datasets_bp)
  app.register_blueprint(files_bp)
  app.register_blueprint(api_bp)
  app.register_blueprint(editor_bp)

  # User loader for Flask-Login
  @login_manager.user_loader
  def load_user(user_id):
    return db.session.get(User, int(user_id))

  def get_user_folder(user_id):
    """Get the user folder path for a specific user"""
    if user_id:
      # Get user email for folder naming
      user = db.session.get(User, user_id)
      if user:
        # Create safe folder name from email (replace special chars)
        safe_email = user.email.replace(
            '@', '_at_').replace('.', '_dot_').replace('-', '_')
        user_dir = os.path.join(app.instance_path, 'users', safe_email)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir
    return None

  def get_user_upload_folder(user_id):
    """Get the upload folder path for a specific user"""
    if user_id:
      user_dir = get_user_folder(user_id)
      if user_dir:
        upload_dir = os.path.join(user_dir, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    # Fallback to global upload folder for anonymous users
    return app.config['UPLOAD_FOLDER']

  def get_user_log_folder(user_id):
    """Get the log folder path for a specific user"""
    if user_id:
      user_dir = get_user_folder(user_id)
      if user_dir:
        log_dir = os.path.join(user_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    return None

  # Models are now defined in models.py

  # Routes are now organized in blueprint files in the routes/ directory

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

  # Create directory structure
  os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Global fallback
  os.makedirs(os.path.join(app.instance_path, 'users'),
              exist_ok=True)  # User folders
  os.makedirs(os.path.join(app.instance_path, 'logs', 'notLogged'),
              exist_ok=True)  # Anonymous logs

  # Create database tables
  with app.app_context():
    db.create_all()

  return app
