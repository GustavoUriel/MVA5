"""
Application Configuration
"""
import os
from datetime import timedelta


class Config:
  """Base configuration class"""

  # Flask Core Settings
  SECRET_KEY = os.environ.get(
      'SECRET_KEY') or 'your-super-secret-key-change-this-in-production'

  # Database Configuration
  DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///microbiome_app.db'
  SQLALCHEMY_DATABASE_URI = DATABASE_URL
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  # Session Configuration
  PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
  SESSION_COOKIE_SECURE = True
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SAMESITE = 'Lax'

  # Google OAuth Configuration
  GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
  GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
  OAUTHLIB_INSECURE_TRANSPORT = os.environ.get(
      'OAUTHLIB_INSECURE_TRANSPORT', '0')

  # Redis Configuration for Celery
  REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
  CELERY_BROKER_URL = REDIS_URL
  CELERY_RESULT_BACKEND = REDIS_URL

  # File Upload Configuration
  MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
  UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
  ALLOWED_EXTENSIONS = {'csv', 'txt', 'tsv', 'xlsx', 'json'}

  # Logging Configuration
  LOG_FOLDER = os.path.join(os.getcwd(), 'logs')
  LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

  # Rate Limiting
  RATELIMIT_STORAGE_URL = REDIS_URL
  RATELIMIT_DEFAULT = "100 per hour"

  # Security Headers
  SECURITY_HEADERS = {
      'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://apis.google.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com"
  }


class DevelopmentConfig(Config):
  """Development configuration"""
  DEBUG = True
  SESSION_COOKIE_SECURE = False
  OAUTHLIB_INSECURE_TRANSPORT = '1'


class ProductionConfig(Config):
  """Production configuration"""
  DEBUG = False
  # Use PostgreSQL in production
  SQLALCHEMY_DATABASE_URI = os.environ.get(
      'DATABASE_URL') or 'postgresql://user:password@localhost/microbiome_db'


class TestingConfig(Config):
  """Testing configuration"""
  TESTING = True
  SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
  WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
