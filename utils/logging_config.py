"""
Logging Configuration and User Activity Tracking
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask import request, session
from extensions import db


def setup_logging(app):
  """Configure application logging"""
  if not app.debug and not app.testing:
    # Create logs directory if it doesn't exist
    log_dir = app.config.get('LOG_FOLDER', 'logs')
    if not os.path.exists(log_dir):
      os.makedirs(log_dir)

    # Set up file handler for application logs
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'microbiome_app.log'),
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microbiome Analysis App startup')


def get_user_log_file(user_id):
  """Get the log file path for a specific user"""
  log_dir = os.path.join(os.getcwd(), 'logs', 'users')
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)

  return os.path.join(log_dir, f'user_{user_id}.log')


def log_user_activity(user_id, action, details=None):
  """Log user activity to database and file"""
  from models import UserLog

  try:
    # Get request information
    ip_address = request.remote_addr if request else None
    user_agent = request.headers.get('User-Agent') if request else None
    session_id = session.get('_id') if session else None

    # Create database log entry
    log_entry = UserLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id,
        timestamp=datetime.utcnow()
    )

    db.session.add(log_entry)
    db.session.commit()

    # Log to user-specific file
    log_to_user_file(user_id, action, details, ip_address, user_agent)

  except Exception as e:
    # Log error but don't fail the main operation
    logging.error(f"Error logging user activity: {str(e)}")


def log_to_user_file(user_id, action, details, ip_address, user_agent):
  """Log activity to user-specific log file"""
  try:
    log_file = get_user_log_file(user_id)

    # Set up user-specific logger
    logger = logging.getLogger(f'user_{user_id}')
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
      logger.removeHandler(handler)

    # Add file handler
    handler = RotatingFileHandler(
        log_file,
        maxBytes=5242880,  # 5MB
        backupCount=5
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Create log message
    log_message = f"Action: {action}"
    if details:
      log_message += f" | Details: {details}"
    if ip_address:
      log_message += f" | IP: {ip_address}"
    if user_agent:
      # Truncate long user agents
      log_message += f" | User-Agent: {user_agent[:100]}..."

    logger.info(log_message)

    # Clean up handler
    logger.removeHandler(handler)
    handler.close()

  except Exception as e:
    logging.error(f"Error writing to user log file: {str(e)}")


def get_user_activity_logs(user_id, limit=100, offset=0):
  """Get user activity logs from database"""
  from models import UserLog

  logs = UserLog.query.filter_by(user_id=user_id)\
      .order_by(UserLog.timestamp.desc())\
      .limit(limit)\
      .offset(offset)\
      .all()

  return [log.to_dict() for log in logs]


def get_user_file_logs(user_id, lines=100):
  """Get recent logs from user's log file"""
  try:
    log_file = get_user_log_file(user_id)

    if not os.path.exists(log_file):
      return []

    with open(log_file, 'r', encoding='utf-8') as f:
      all_lines = f.readlines()
      return all_lines[-lines:] if len(all_lines) > lines else all_lines

  except Exception as e:
    logging.error(f"Error reading user log file: {str(e)}")
    return []
