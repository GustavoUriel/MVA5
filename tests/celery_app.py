"""
Celery application configuration for Microbiome Analysis Platform
"""

import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Celery instance
celery_app = Celery('microbiome_analysis')

# Configuration
celery_app.conf.update(
    broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    include=[
        'tasks.data_processing',
        'tasks.analysis',
        'tasks.notifications'
    ],
    task_routes={
        'tasks.data_processing.*': {'queue': 'data_processing'},
        'tasks.analysis.*': {'queue': 'analysis'},
        'tasks.notifications.*': {'queue': 'notifications'},
    },
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    task_soft_time_limit=3600,  # 1 hour
    task_time_limit=7200,  # 2 hours
    result_expires=3600,  # 1 hour
)

# Task result configuration
celery_app.conf.result_backend_transport_options = {
    'master_name': 'mymaster',
    'visibility_timeout': 3600,
}

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-expired-sessions': {
        'task': 'tasks.maintenance.cleanup_expired_sessions',
        'schedule': 3600.0,  # Every hour
    },
    'cleanup-old-results': {
        'task': 'tasks.maintenance.cleanup_old_results',
        'schedule': 86400.0,  # Every day
    },
    'health-check': {
        'task': 'tasks.maintenance.health_check',
        'schedule': 300.0,  # Every 5 minutes
    },
}

if __name__ == '__main__':
    celery_app.start()
