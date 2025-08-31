"""
Cleanup script for old files and logs
Can be run as a scheduled task
"""

from tasks.analysis_tasks import cleanup_old_files
from app import create_app
import os
import sys
from datetime import datetime, timedelta

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
  app = create_app()
  with app.app_context():
    result = cleanup_old_files.delay()
    print(f"Cleanup task started: {result.id}")
    print("Task will run in background via Celery")
