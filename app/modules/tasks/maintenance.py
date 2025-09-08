"""
Maintenance tasks for the Microbiome Analysis Platform
"""

from celery import current_app
import logging
import os
import traceback
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def log_task_error(task_name, exception, context=None, extra_data=None):
    """
    Log task errors with comprehensive context
    
    Args:
        task_name: Name of the task that failed
        exception: The exception object
        context: Additional context about the error
        extra_data: Additional data to include in the log
    """
    error_data = {
        'task_name': task_name,
        'exception_type': type(exception).__name__,
        'exception_message': str(exception),
        'context': context,
        'extra_data': extra_data,
        'timestamp': datetime.utcnow().isoformat(),
        'stack_trace': traceback.format_exc()
    }
    
    logger.error(
        f"Celery task failed: {task_name} - {type(exception).__name__}: {str(exception)}",
        extra={'task_error_data': error_data},
        exc_info=True
    )

@current_app.task
def cleanup_expired_sessions():
    """Clean up expired user sessions"""
    task_name = "cleanup_expired_sessions"
    try:
        logger.info(f"Starting task: {task_name}")
        start_time = datetime.utcnow()
        
        # This would connect to Redis and clean up expired sessions
        # For now, cleaning up filesystem sessions
        session_dir = os.path.join(os.getcwd(), 'flask_session')
        cleaned_count = 0
        
        if os.path.exists(session_dir):
            cutoff_time = datetime.now() - timedelta(hours=24)  # 24 hours ago
            for filename in os.listdir(session_dir):
                file_path = os.path.join(session_dir, filename)
                if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time.timestamp():
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                        logger.debug(f"Removed expired session file: {filename}")
                    except OSError as file_error:
                        logger.warning(f"Could not remove session file {filename}: {file_error}")
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        result = {
            "status": "success", 
            "message": f"Expired sessions cleaned up - {cleaned_count} files removed",
            "files_removed": cleaned_count,
            "duration_seconds": duration
        }
        
        logger.info(f"Task {task_name} completed successfully in {duration:.2f}s - {cleaned_count} files removed")
        return result
        
    except Exception as e:
        log_task_error(
            task_name,
            e,
            context="Cleaning up expired user sessions",
            extra_data={
                'session_directory': os.path.join(os.getcwd(), 'flask_session'),
                'cutoff_hours': 24
            }
        )
        return {"status": "error", "message": str(e), "task_name": task_name}

@current_app.task
def cleanup_old_results():
    """Clean up old analysis results and temporary files"""
    task_name = "cleanup_old_results"
    try:
        logger.info(f"Starting task: {task_name}")
        start_time = datetime.utcnow()
        
        # Clean up old files from uploads directory
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        cleaned_count = 0
        total_size_freed = 0
        
        if os.path.exists(upload_dir):
            cutoff_time = datetime.now() - timedelta(days=30)  # 30 days ago
            
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                
                if os.path.isfile(file_path):
                    try:
                        file_mtime = os.path.getmtime(file_path)
                        if file_mtime < cutoff_time.timestamp():
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            cleaned_count += 1
                            total_size_freed += file_size
                            logger.debug(f"Removed old file: {filename} ({file_size} bytes)")
                    except OSError as file_error:
                        logger.warning(f"Could not remove file {filename}: {file_error}")
                        
        duration = (datetime.utcnow() - start_time).total_seconds()
        result = {
            "status": "success", 
            "message": f"Old results cleaned up - {cleaned_count} files removed",
            "files_removed": cleaned_count,
            "size_freed_bytes": total_size_freed,
            "size_freed_mb": round(total_size_freed / (1024 * 1024), 2),
            "duration_seconds": duration
        }
        
        logger.info(f"Task {task_name} completed successfully in {duration:.2f}s - "
                   f"{cleaned_count} files removed, {result['size_freed_mb']} MB freed")
        return result
        
    except Exception as e:
        log_task_error(
            task_name,
            e,
            context="Cleaning up old analysis results and temporary files",
            extra_data={
                'upload_directory': os.path.join(os.getcwd(), 'uploads'),
                'cutoff_days': 30
            }
        )
        return {"status": "error", "message": str(e), "task_name": task_name}

@current_app.task
def health_check():
    """Perform system health check"""
    task_name = "health_check"
    try:
        logger.info(f"Starting task: {task_name}")
        start_time = datetime.utcnow()
        
        health_issues = []
        warnings = []
        
        # Check disk space
        try:
            disk_usage = os.statvfs('.')
            free_space = disk_usage.f_frsize * disk_usage.f_bavail
            free_space_gb = free_space / (1024*1024*1024)
            
            # Check if we have at least 1GB free
            if free_space_gb < 1:
                health_issues.append(f"Critical: Low disk space - {free_space_gb:.2f} GB remaining")
                logger.error(f"Critical disk space warning: {free_space_gb:.2f} GB remaining")
            elif free_space_gb < 5:
                warnings.append(f"Warning: Low disk space - {free_space_gb:.2f} GB remaining")
                logger.warning(f"Low disk space warning: {free_space_gb:.2f} GB remaining")
                
        except Exception as disk_error:
            health_issues.append(f"Could not check disk space: {str(disk_error)}")
            logger.error(f"Disk space check failed: {disk_error}")
            free_space_gb = None
        
        # Check upload directory
        try:
            upload_dir = os.path.join(os.getcwd(), 'uploads')
            if not os.path.exists(upload_dir):
                warnings.append("Upload directory does not exist")
            elif not os.access(upload_dir, os.W_OK):
                health_issues.append("Upload directory is not writable")
        except Exception as upload_error:
            health_issues.append(f"Could not check upload directory: {str(upload_error)}")
            logger.error(f"Upload directory check failed: {upload_error}")
        
        # Check log directory
        try:
            log_dir = os.path.join(os.getcwd(), 'instance', 'logs')
            if not os.path.exists(log_dir):
                warnings.append("Log directory does not exist")
            elif not os.access(log_dir, os.W_OK):
                health_issues.append("Log directory is not writable")
        except Exception as log_error:
            health_issues.append(f"Could not check log directory: {str(log_error)}")
            logger.error(f"Log directory check failed: {log_error}")
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Determine overall status
        if health_issues:
            status = "critical"
            logger.error(f"Health check found critical issues: {health_issues}")
        elif warnings:
            status = "warning"
            logger.warning(f"Health check found warnings: {warnings}")
        else:
            status = "healthy"
            logger.info("Health check passed - all systems normal")
        
        result = {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "free_space_gb": free_space_gb,
            "health_issues": health_issues,
            "warnings": warnings,
            "duration_seconds": duration,
            "task_name": task_name
        }
        
        logger.info(f"Task {task_name} completed in {duration:.2f}s - Status: {status}")
        return result
        
    except Exception as e:
        log_task_error(
            task_name,
            e,
            context="Performing system health check",
            extra_data={
                'checks_performed': ['disk_space', 'upload_directory', 'log_directory']
            }
        )
        return {
            "status": "error", 
            "message": str(e), 
            "task_name": task_name,
            "timestamp": datetime.utcnow().isoformat()
        }
