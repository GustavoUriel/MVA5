"""
Celery Worker Entry Point
"""
from app import create_app
from extensions import celery_app

# Create Flask app instance
flask_app = create_app()

# Configure Celery with Flask app context
with flask_app.app_context():
  celery_app.conf.update(flask_app.config)
