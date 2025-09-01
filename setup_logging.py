#!/usr/bin/env python3
"""
Setup script for creating log directory structure
Run this script to ensure all required log directories exist
"""

import os
import sys

def create_log_directories():
    """Create all required log directories"""
    
    # Base directory for logs
    instance_dir = 'instance'
    log_base_dir = os.path.join(instance_dir, 'logs')
    
    # All required log directories
    directories = [
        log_base_dir,
        os.path.join(log_base_dir, 'users'),
        os.path.join(log_base_dir, 'system'),
        os.path.join(log_base_dir, 'errors'),
        os.path.join(log_base_dir, 'audit'),
        os.path.join(log_base_dir, 'performance'),
        os.path.join(log_base_dir, 'celery'),
    ]
    
    created_dirs = []
    existing_dirs = []
    
    for directory in directories:
        if os.path.exists(directory):
            existing_dirs.append(directory)
            print(f"✓ Directory already exists: {directory}")
        else:
            try:
                os.makedirs(directory, exist_ok=True)
                created_dirs.append(directory)
                print(f"✓ Created directory: {directory}")
            except Exception as e:
                print(f"✗ Failed to create directory {directory}: {e}")
                return False
    
    # Create .gitignore file for logs to prevent committing sensitive information
    gitignore_path = os.path.join(log_base_dir, '.gitignore')
    gitignore_content = """# Ignore all log files but keep directory structure
*.log
*.log.*
users/
system/
errors/
audit/
performance/
celery/

# Keep .gitignore and README
!.gitignore
!README.md
"""
    
    try:
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print(f"✓ Created .gitignore: {gitignore_path}")
    except Exception as e:
        print(f"✗ Failed to create .gitignore: {e}")
    
    # Create README file explaining log structure
    readme_path = os.path.join(log_base_dir, 'README.md')
    readme_content = """# Application Logs

This directory contains all application logs organized by category:

## Directory Structure

- **users/**: User-specific log files (format: `user_{user_id}.log`)
- **system/**: System-wide logs including performance metrics
- **errors/**: Critical error logs and stack traces
- **audit/**: Security and compliance audit logs
- **performance/**: Performance monitoring and timing logs
- **celery/**: Background task logs

## Log File Naming Convention

- User logs: `users/user_{user_id}.log`
- System logs: `system/system.log`
- Error logs: `errors/errors.log`
- Audit logs: `audit/audit.log`
- Performance logs: `system/performance.log`

## Log Rotation

All log files are automatically rotated when they reach size limits:
- User logs: 10MB, 5 backups
- System logs: 50MB, 10 backups
- Error logs: 50MB, 10 backups
- Audit logs: 100MB, 20 backups

## Security Note

Log files may contain sensitive information and should be protected appropriately.
This directory is excluded from version control via .gitignore.
"""
    
    try:
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"✓ Created README: {readme_path}")
    except Exception as e:
        print(f"✗ Failed to create README: {e}")
    
    print(f"\n📊 Summary:")
    print(f"  - Created directories: {len(created_dirs)}")
    print(f"  - Existing directories: {len(existing_dirs)}")
    print(f"  - Total directories: {len(directories)}")
    
    if created_dirs:
        print(f"\n📁 New directories created:")
        for dir_path in created_dirs:
            print(f"    {dir_path}")
    
    return True

def verify_permissions():
    """Verify that the application can write to log directories"""
    print("\n🔐 Verifying write permissions...")
    
    log_base_dir = os.path.join('instance', 'logs')
    test_dirs = [
        os.path.join(log_base_dir, 'users'),
        os.path.join(log_base_dir, 'system'),
        os.path.join(log_base_dir, 'errors'),
        os.path.join(log_base_dir, 'audit'),
    ]
    
    all_good = True
    
    for test_dir in test_dirs:
        test_file = os.path.join(test_dir, 'permission_test.tmp')
        try:
            with open(test_file, 'w') as f:
                f.write("permission test")
            os.remove(test_file)
            print(f"✓ Write permission OK: {test_dir}")
        except Exception as e:
            print(f"✗ Write permission FAILED: {test_dir} - {e}")
            all_good = False
    
    return all_good

def main():
    """Main setup function"""
    print("🚀 Setting up logging infrastructure...")
    print("=" * 50)
    
    # Create directories
    if not create_log_directories():
        print("\n❌ Failed to create some directories!")
        sys.exit(1)
    
    # Verify permissions
    if not verify_permissions():
        print("\n❌ Permission verification failed!")
        sys.exit(1)
    
    print("\n✅ Logging setup completed successfully!")
    print("\n📋 Next steps:")
    print("  1. Run your Flask application")
    print("  2. Check that logs are being created in instance/logs/")
    print("  3. Monitor log files for any issues")
    print("\n💡 Tips:")
    print("  - User-specific logs will be created when users perform actions")
    print("  - System logs will contain application-wide events")
    print("  - Error logs will capture all exceptions with full stack traces")
    print("  - Audit logs will track security-relevant events")

if __name__ == '__main__':
    main()
