"""
Comprehensive logging configuration for Microbiome Analysis Platform
Provides user-specific logging and system-wide error tracking
"""

import logging
import logging.handlers
import os
import traceback
import sys
from datetime import datetime
from flask import current_app, session, request
from flask_login import current_user
import json
import uuid


class UserAwareFormatter(logging.Formatter):
    """Custom formatter that includes user context in log messages"""
    
    def format(self, record):
        # Add user context to the record
        try:
            # Prevent infinite logging loop by checking if we're already in a database operation
            if (hasattr(current_user, '_sa_instance_state') and 
                hasattr(current_user, 'is_authenticated') and 
                current_user.is_authenticated and
                not getattr(record, '_avoid_db_access', False)):
                # Safely access user info without triggering database queries
                user_id = getattr(current_user, '_sa_instance_state').key[1] if current_user._sa_instance_state.key else 'unknown'
                record.user_id = user_id
                record.user_email = getattr(current_user, 'email', 'unknown') if hasattr(current_user, 'email') else 'unknown'
            else:
                record.user_id = 'anonymous'
                record.user_email = 'anonymous'
        except Exception:
            record.user_id = 'system'
            record.user_email = 'system'
        
        # Add request context
        try:
            if request:
                record.request_id = getattr(request, 'request_id', str(uuid.uuid4())[:8])
                record.ip_address = request.remote_addr
                record.user_agent = request.headers.get('User-Agent', 'unknown')[:100]
                record.endpoint = request.endpoint or 'unknown'
                record.method = request.method
                record.url = request.url
            else:
                record.request_id = 'no_request'
                record.ip_address = 'unknown'
                record.user_agent = 'unknown'
                record.endpoint = 'unknown'
                record.method = 'unknown'
                record.url = 'unknown'
        except Exception:
            record.request_id = 'no_request'
            record.ip_address = 'unknown'
            record.user_agent = 'unknown'
            record.endpoint = 'unknown'
            record.method = 'unknown'
            record.url = 'unknown'
        
        # Add stack trace for errors
        if record.levelno >= logging.ERROR and record.exc_info:
            record.stack_trace = ''.join(traceback.format_exception(*record.exc_info))
        else:
            record.stack_trace = ''
        
        return super().format(record)


class UserSpecificHandler(logging.Handler):
    """Custom handler that routes logs to user-specific files"""
    
    def __init__(self, log_dir='logs', instance_path=None):
        super().__init__()
        self.log_dir = log_dir
        self.instance_path = instance_path
        self.handlers = {}
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(os.path.join(log_dir, 'notLogged'), exist_ok=True)
        os.makedirs(os.path.join(log_dir, 'system'), exist_ok=True)
        if instance_path:
            os.makedirs(os.path.join(instance_path, 'users'), exist_ok=True)
    
    def emit(self, record):
        try:
            # Determine which file to log to
            if hasattr(record, 'user_id') and record.user_id not in ['anonymous', 'system']:
                # Get user email for folder naming
                try:
                    from app import User
                    user = User.query.get(int(record.user_id))
                    if user:
                        # Create safe folder name from email
                        safe_email = user.email.replace('@', '_at_').replace('.', '_dot_').replace('-', '_')
                        user_dir = os.path.join(self.instance_path, 'users', safe_email, 'logs')
                        os.makedirs(user_dir, exist_ok=True)
                        log_file = os.path.join(user_dir, 'user.log')
                    else:
                        # Fallback to system logs if user not found
                        log_file = os.path.join(self.log_dir, 'system', 'system.log')
                except Exception:
                    # Fallback to system logs if error getting user
                    log_file = os.path.join(self.log_dir, 'system', 'system.log')
            elif hasattr(record, 'user_id') and record.user_id == 'anonymous':
                # Log to notLogged directory for anonymous users
                log_file = os.path.join(self.log_dir, 'notLogged', 'anonymous.log')
            else:
                # System logs
                log_file = os.path.join(self.log_dir, 'system', 'system.log')
            
            # Get or create handler for this file
            if log_file not in self.handlers:
                # Create rotating file handler
                handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5,
                    encoding='utf-8'
                )
                formatter = UserAwareFormatter(
                    fmt='%(asctime)s - %(levelname)s - [%(user_id)s:%(user_email)s] - '
                        '[%(request_id)s] - %(endpoint)s - %(method)s - '
                        '%(filename)s:%(lineno)d - %(funcName)s - %(message)s'
                        '%(stack_trace)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                handler.setFormatter(formatter)
                self.handlers[log_file] = handler
            
            # Emit to the appropriate handler
            self.handlers[log_file].emit(record)
            
        except Exception:
            self.handleError(record)


class ErrorLogger:
    """Centralized error logging utility"""
    
    @staticmethod
    def log_exception(exception, context=None, user_action=None, extra_data=None):
        """
        Log an exception with comprehensive context
        
        Args:
            exception: The exception object
            context: Additional context about where the error occurred
            user_action: What the user was trying to do when the error occurred
            extra_data: Additional data to include in the log
        """
        logger = logging.getLogger('error_tracker')
        
        error_data = {
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'context': context,
            'user_action': user_action,
            'extra_data': extra_data,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        # Add stack trace
        error_data['stack_trace'] = traceback.format_exc()
        
        # Add request context if available
        try:
            if request:
                error_data['request_data'] = {
                    'url': request.url,
                    'method': request.method,
                    'endpoint': request.endpoint,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent'),
                    'referrer': request.referrer,
                    'form_data': dict(request.form) if request.form else None,
                    'args': dict(request.args) if request.args else None
                }
        except Exception:
            error_data['request_data'] = None
        
        # Add user context if available
        try:
            if hasattr(current_user, 'id') and current_user.is_authenticated:
                error_data['user_context'] = {
                    'user_id': current_user.id,
                    'user_email': current_user.email,
                    'user_name': current_user.name
                }
        except Exception:
            error_data['user_context'] = None
        
        # Log the error
        logger.error(
            f"Exception occurred: {type(exception).__name__}: {str(exception)}",
            extra={'error_data': json.dumps(error_data, indent=2)},
            exc_info=True
        )
        
        return error_data
    
    @staticmethod
    def log_warning(message, context=None, user_action=None, extra_data=None):
        """Log a warning with context"""
        logger = logging.getLogger('error_tracker')
        
        warning_data = {
            'message': message,
            'context': context,
            'user_action': user_action,
            'extra_data': extra_data,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        logger.warning(
            f"Warning: {message}",
            extra={'warning_data': json.dumps(warning_data, indent=2)}
        )


def setup_logging(app):
    """
    Set up comprehensive logging for the Flask application
    
    Args:
        app: Flask application instance
    """
    
    # Create logs directory structure
    log_dir = os.path.join(app.instance_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(os.path.join(log_dir, 'notLogged'), exist_ok=True)
    os.makedirs(os.path.join(log_dir, 'users'), exist_ok=True)
    os.makedirs(os.path.join(log_dir, 'system'), exist_ok=True)
    os.makedirs(os.path.join(log_dir, 'errors'), exist_ok=True)
    os.makedirs(os.path.join(log_dir, 'audit'), exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 1. Console handler for development
    if app.debug:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
    
    # 2. User-specific logging handler
    user_handler = UserSpecificHandler(log_dir, app.instance_path)
    user_handler.setLevel(logging.INFO)
    root_logger.addHandler(user_handler)
    
    # 3. System error handler (for critical errors)
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'errors', 'errors.log'),
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10,
        encoding='utf-8'
    )
    error_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - '
        '%(funcName)s - %(message)s\n%(stack_trace)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    error_handler.setFormatter(UserAwareFormatter(error_formatter._fmt))
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)
    
    # 4. Audit log handler (for security and compliance)
    audit_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'audit', 'audit.log'),
        maxBytes=100*1024*1024,  # 100MB
        backupCount=20,
        encoding='utf-8'
    )
    audit_formatter = logging.Formatter(
        '%(asctime)s - AUDIT - [%(user_id)s:%(user_email)s] - '
        '[%(request_id)s] - %(ip_address)s - %(method)s %(url)s - '
        '%(endpoint)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    audit_handler.setFormatter(UserAwareFormatter(audit_formatter._fmt))
    audit_handler.setLevel(logging.INFO)
    
    # Create audit logger
    audit_logger = logging.getLogger('audit')
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)
    
    # 5. Performance log handler
    perf_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'system', 'performance.log'),
        maxBytes=50*1024*1024,  # 50MB
        backupCount=5,
        encoding='utf-8'
    )
    perf_formatter = logging.Formatter(
        '%(asctime)s - PERFORMANCE - [%(user_id)s] - [%(request_id)s] - '
        '%(endpoint)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    perf_handler.setFormatter(UserAwareFormatter(perf_formatter._fmt))
    
    # Create performance logger
    perf_logger = logging.getLogger('performance')
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)
    
    # Configure specific loggers
    
    # Flask app logger
    app.logger.setLevel(logging.INFO)
    
    # SQLAlchemy logger (for database operations)
    db_logger = logging.getLogger('sqlalchemy.engine')
    if app.debug:
        db_logger.setLevel(logging.INFO)
    else:
        db_logger.setLevel(logging.WARNING)
    
    # Werkzeug logger (for HTTP requests)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    
    # Celery logger
    celery_logger = logging.getLogger('celery')
    celery_logger.setLevel(logging.INFO)
    
    app.logger.info(f"Logging setup completed. Log directory: {log_dir}")


def log_user_action(action, details=None, success=True, duration=None):
    """
    Log user actions for audit trail
    
    Args:
        action: The action performed (login, logout, upload, etc.)
        details: Additional details about the action
        success: Whether the action was successful
        duration: Time taken for the action (in seconds)
    """
    audit_logger = logging.getLogger('audit')
    
    message = f"User action: {action}"
    if details:
        message += f" - {details}"
    if not success:
        message += " - FAILED"
    if duration:
        message += f" - Duration: {duration:.2f}s"
    
    if success:
        audit_logger.info(message)
    else:
        audit_logger.warning(message)


def log_performance(operation, duration, details=None):
    """
    Log performance metrics
    
    Args:
        operation: The operation being measured
        duration: Time taken in seconds
        details: Additional details about the operation
    """
    perf_logger = logging.getLogger('performance')
    
    message = f"Operation: {operation} - Duration: {duration:.2f}s"
    if details:
        message += f" - {details}"
    
    # Log as warning if operation takes too long
    if duration > 5:  # 5 seconds threshold
        perf_logger.warning(f"SLOW {message}")
    else:
        perf_logger.info(message)


# Decorator for automatic error logging
def log_errors(func):
    """Decorator to automatically log errors from functions"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorLogger.log_exception(
                e,
                context=f"Function: {func.__name__}",
                user_action=f"Executing {func.__name__}",
                extra_data={'args': str(args), 'kwargs': str(kwargs)}
            )
            raise
    return wrapper


# Context manager for performance logging
class PerformanceTracker:
    """Context manager for tracking operation performance"""
    
    def __init__(self, operation_name, details=None):
        self.operation_name = operation_name
        self.details = details
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            log_performance(self.operation_name, duration, self.details)
        
        if exc_type:
            ErrorLogger.log_exception(
                exc_val,
                context=f"Performance tracked operation: {self.operation_name}",
                extra_data={'details': self.details}
            )
