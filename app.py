"""
Flask Application Entry Point
Microbiome Analysis Web Application
"""

import os
from flask import Flask
from config import Config
from extensions import db, login_manager, migrate, celery_app, limiter
from auth.routes import auth_bp, init_oauth
from datasets.routes import datasets_bp
from utils.logging_config import setup_logging
from models import User


def create_app(config_class=Config):
  """Application factory pattern"""
  app = Flask(__name__)
  app.config.from_object(config_class)

  # Load environment variables
  from dotenv import load_dotenv
  load_dotenv()

  # Update config with environment variables
  app.config.update({
      'SECRET_KEY': os.getenv('SECRET_KEY', app.config['SECRET_KEY']),
      'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
      'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
      'OAUTHLIB_INSECURE_TRANSPORT': os.getenv('OAUTHLIB_INSECURE_TRANSPORT', '0'),
      'DATABASE_URL': os.getenv('DATABASE_URL', app.config['DATABASE_URL']),
      'REDIS_URL': os.getenv('REDIS_URL', app.config['REDIS_URL']),
      'UPLOAD_FOLDER': os.getenv('UPLOAD_FOLDER', app.config['UPLOAD_FOLDER']),
      'LOG_FOLDER': os.getenv('LOG_FOLDER', app.config['LOG_FOLDER']),
  })

  # Ensure required directories exist
  os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
  os.makedirs(app.config['LOG_FOLDER'], exist_ok=True)

  # Initialize extensions
  db.init_app(app)
  login_manager.init_app(app)
  migrate.init_app(app, db)
  limiter.init_app(app)

  # Configure Celery
  celery_app.conf.update(app.config)

  # Set up logging
  setup_logging(app)

  # Initialize OAuth
  init_oauth(app)

  # Register blueprints
  app.register_blueprint(auth_bp, url_prefix='/auth')
  app.register_blueprint(datasets_bp, url_prefix='/datasets')

  # User loader for Flask-Login
  @login_manager.user_loader
  def load_user(user_id):
    return User.query.get(int(user_id))

  @login_manager.unauthorized_handler
  def unauthorized():
    from flask import redirect, url_for, session, request
    # Store the original URL to redirect after login
    if request.endpoint != 'auth.login':
      session['next_page'] = request.url
    return redirect(url_for('auth.login'))

  # Main route
  @app.route('/')
  def index():
    from flask import redirect, url_for
    from flask_login import current_user

    if current_user.is_authenticated:
      return redirect(url_for('datasets.dashboard'))
    return redirect(url_for('auth.login'))

  # Security headers
  @app.after_request
  def add_security_headers(response):
    for header, value in app.config.get('SECURITY_HEADERS', {}).items():
      response.headers[header] = value
    return response

  # Create tables
  with app.app_context():
    db.create_all()

  return app


if __name__ == '__main__':
  app = create_app()
  # Default to port 5002, allow override via PORT environment variable
  port = int(os.getenv('PORT', 5002))
  host = os.getenv('HOST', '0.0.0.0')
  # Respect FLASK_DEBUG or DEBUG environment variable
  debug_env = os.getenv('FLASK_DEBUG') or os.getenv('DEBUG')
  debug = True if str(debug_env).lower() in ('1', 'true', 'yes') else False
  app.run(host=host, port=port, debug=debug)
