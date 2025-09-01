# Comprehensive Error Logging Implementation

## Overview

This implementation provides comprehensive error logging across your Flask microbiome analysis application with the following key features:

- **User-specific logging**: Separate log files for each user
- **System-wide logging**: Central logging for anonymous/system events
- **Comprehensive error tracking**: Full stack traces for every exception
- **Performance monitoring**: Request timing and operation performance
- **Audit trail**: Security and compliance logging
- **Automatic log rotation**: Prevents disk space issues

## Architecture

### Log Directory Structure

```
instance/logs/
├── users/           # User-specific log files
│   ├── user_1.log
│   ├── user_2.log
│   └── ...
├── system/          # System-wide logs
│   ├── system.log
│   └── performance.log
├── errors/          # Critical error logs
│   └── errors.log
├── audit/           # Security audit logs
│   └── audit.log
├── performance/     # Performance monitoring
└── celery/         # Background task logs
```

### Log File Types

1. **User Logs** (`users/user_{id}.log`)
   - All user-specific actions and errors
   - Rotated at 10MB, 5 backups retained
   - Format includes user context and request information

2. **System Logs** (`system/system.log`)
   - Anonymous user actions
   - System-wide events
   - Application startup/shutdown events

3. **Error Logs** (`errors/errors.log`)
   - All exceptions with full stack traces
   - Critical system errors
   - Rotated at 50MB, 10 backups retained

4. **Audit Logs** (`audit/audit.log`)
   - Security-relevant events
   - User authentication/authorization
   - Data access and modifications
   - Rotated at 100MB, 20 backups retained

5. **Performance Logs** (`system/performance.log`)
   - Request timing information
   - Slow operation warnings (>5 seconds)
   - Database query performance

## Key Components

### 1. ErrorLogger Class (`logging_config.py`)

The `ErrorLogger` class provides centralized error logging with comprehensive context:

```python
from logging_config import ErrorLogger

# Log an exception with context
ErrorLogger.log_exception(
    exception,
    context="Description of what was happening",
    user_action="What the user was trying to do",
    extra_data={"key": "value"}
)

# Log a warning
ErrorLogger.log_warning(
    "Warning message",
    context="Context information",
    user_action="User action",
    extra_data={"additional": "data"}
)
```

### 2. Performance Tracking

Use the `PerformanceTracker` context manager for timing operations:

```python
from logging_config import PerformanceTracker

with PerformanceTracker("operation_name", "additional details"):
    # Your code here
    perform_expensive_operation()
```

### 3. User Action Logging

Track user actions for audit purposes:

```python
from logging_config import log_user_action

log_user_action("action_name", "details", success=True, duration=1.5)
```

### 4. Automatic Error Logging Decorator

Use the `@log_errors` decorator for automatic error logging:

```python
from logging_config import log_errors

@log_errors
def my_function():
    # Function code here
    pass
```

## Implementation Details

### 1. Application Integration

The logging system is integrated into `app.py` with:

- **Request tracking**: Every HTTP request is tracked with unique IDs
- **Performance monitoring**: Request timing and slow request detection
- **Comprehensive error handlers**: All HTTP error codes have detailed logging
- **User context**: Automatic user identification in all logs

### 2. Database Operations

All database operations now include:
- Transaction tracking
- Error logging with rollback information
- Performance monitoring for slow queries

### 3. Authentication Events

OAuth and login/logout events are fully logged with:
- Success/failure tracking
- Security context (IP, user agent)
- Timing information
- Error details for failed attempts

### 4. Celery Task Logging

Background tasks include:
- Task start/completion logging
- Error handling with full context
- Performance monitoring
- Health check results

## Log Format Examples

### User-Specific Log Entry
```
2024-01-15 10:30:45 - ERROR - [123:user@example.com] - [req_abc123] - new_dataset - POST - app.py:183 - new_dataset - Exception occurred: ValidationError: Dataset name already exists
Stack trace:
Traceback (most recent call last):
  File "/app/app.py", line 175, in new_dataset
    db.session.commit()
ValidationError: Dataset name already exists
```

### Audit Log Entry
```
2024-01-15 10:30:45 - AUDIT - [123:user@example.com] - [req_abc123] - 192.168.1.100 - POST /auth/login - auth_callback - User action: user_login - Successful login: user@example.com
```

### Performance Log Entry
```
2024-01-15 10:30:45 - PERFORMANCE - [123] - [req_abc123] - dataset_creation - Operation: POST new_dataset - Duration: 2.34s - Status: 200
```

## Error Context Information

Every logged error includes:

### Exception Details
- Exception type and message
- Full stack trace
- Timestamp (UTC)

### Request Context
- HTTP method and URL
- Request ID for tracing
- User agent and IP address
- Form data and query parameters (sanitized)

### User Context
- User ID and email (if authenticated)
- User actions being performed
- Session information

### System Context
- Database transaction state
- Performance metrics
- Additional custom data

## Configuration

### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about application flow
- **WARNING**: Something unexpected happened but application continues
- **ERROR**: Serious problem that prevented a function from completing
- **CRITICAL**: Very serious error that may prevent the application from running

### Log Rotation
- Automatic rotation based on file size
- Configurable backup retention
- Different policies for different log types

## Monitoring and Alerting

### Key Metrics to Monitor
1. **Error Rate**: Number of errors per hour/day
2. **Performance**: Slow requests (>5 seconds)
3. **Disk Usage**: Log directory size
4. **Failed Logins**: Security monitoring

### Log Analysis Queries

**Find all errors for a specific user:**
```bash
grep "user_123" instance/logs/users/user_123.log | grep "ERROR"
```

**Find slow operations:**
```bash
grep "SLOW" instance/logs/system/performance.log
```

**Security audit:**
```bash
grep "FAILED" instance/logs/audit/audit.log
```

## Setup Instructions

1. **Install Dependencies**: All logging dependencies are included in the main application

2. **Run Setup Script**:
   ```bash
   python setup_logging.py
   ```

3. **Verify Installation**: Check that log directories exist in `instance/logs/`

4. **Start Application**: Logs will be created automatically when the application runs

## Maintenance

### Log Cleanup
The system includes automatic cleanup via Celery tasks:
- Session cleanup every hour
- Old file cleanup daily
- Health checks every 5 minutes

### Manual Cleanup
```bash
# Clean old log files (older than 30 days)
find instance/logs/ -name "*.log.*" -mtime +30 -delete

# Check disk usage
du -sh instance/logs/
```

### Log Analysis Tools
- Use `tail -f` to monitor logs in real-time
- Use `grep` for searching specific patterns
- Use log analysis tools like ELK stack for advanced monitoring

## Security Considerations

1. **Sensitive Data**: Logs may contain sensitive information - secure appropriately
2. **Access Control**: Restrict access to log files
3. **Retention Policy**: Implement appropriate log retention policies
4. **Compliance**: Ensure logging meets regulatory requirements

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure application has write access to log directories
2. **Disk Space**: Monitor disk usage and implement cleanup policies
3. **Performance Impact**: Logging adds minimal overhead but monitor if needed

### Debug Mode
Enable debug logging by setting the environment variable:
```bash
export LOG_LEVEL=DEBUG
```

## Best Practices

1. **Error Handling**: Always use try-except blocks with proper logging
2. **Context**: Include relevant context in error messages
3. **Performance**: Use PerformanceTracker for timing critical operations
4. **Security**: Log security-relevant events for audit purposes
5. **Monitoring**: Regularly review logs for patterns and issues

## Future Enhancements

1. **Centralized Logging**: Consider ELK stack or similar for production
2. **Real-time Monitoring**: Implement alerts for critical errors
3. **Log Aggregation**: Collect logs from multiple application instances
4. **Metrics Dashboard**: Create visualization for log metrics
5. **Machine Learning**: Implement anomaly detection on log patterns
