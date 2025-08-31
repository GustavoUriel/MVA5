"""
Flask Extensions Initialization
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery
import redis


# Database
db = SQLAlchemy()

# Authentication
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Database migrations
migrate = Migrate()

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Celery for background tasks


def make_celery(app=None):
  """Create Celery instance"""
  celery = Celery(
      'microbiome_app',
      broker='redis://localhost:6379/0',
      backend='redis://localhost:6379/0'
  )

  if app:
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
      """Make celery tasks work with Flask app context"""

      def __call__(self, *args, **kwargs):
        with app.app_context():
          return self.run(*args, **kwargs)

    celery.Task = ContextTask

  return celery


# Initialize Celery
celery_app = make_celery()

# Redis client
redis_client = redis.Redis(host='localhost', port=6379,
                           db=0, decode_responses=True)
