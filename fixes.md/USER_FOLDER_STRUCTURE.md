# User-Specific Folder Structure

## Overview

The application now implements a user-specific folder structure that organizes logs and uploads by user, providing better isolation and organization of user data.

## Folder Structure

```
instance/
├── users/                  # User-specific folders
│   ├── user_at_example_dot_com/  # User email: user@example.com
│   │   ├── logs/          # User's activity logs
│   │   │   └── user.log
│   │   └── uploads/       # User's uploaded files
│   │       ├── 1_patients_1234567890.csv
│   │       ├── 1_taxonomy_1234567891.csv
│   │       └── 1_bracken_1234567892.csv
│   ├── admin_at_company_dot_org/  # User email: admin@company.org
│   │   ├── logs/
│   │   │   └── user.log
│   │   └── uploads/
│   └── ...
├── logs/                   # System and anonymous logs
│   ├── notLogged/         # Logs for anonymous/unauthenticated users
│   │   └── anonymous.log
│   ├── system/            # System-wide logs
│   │   ├── system.log
│   │   └── performance.log
│   ├── errors/            # Error logs
│   │   └── errors.log
│   └── audit/             # Audit logs
│       └── audit.log
└── uploads/               # Global fallback upload folder
```

## Key Features

### 🔐 **User Isolation**
- Each user gets their own folder: `instance/users/{safe_email}/`
- User uploads are stored in: `instance/users/{safe_email}/uploads/`
- User logs are stored in: `instance/users/{safe_email}/logs/user.log`

### 📝 **Anonymous User Handling**
- Unauthenticated users' logs go to: `instance/logs/notLogged/anonymous.log`
- Anonymous uploads use the global fallback folder: `instance/uploads/`

### 🗂️ **Automatic Directory Creation**
- User directories are created automatically when the user logs in
- Upload folders are created when the user uploads their first file
- All directories are created with proper permissions

## Implementation Details

### Backend Changes

#### 1. **User Folder Functions**
```python
def get_user_folder(user_id):
    """Get the user folder path for a specific user"""
    if user_id:
        # Get user email for folder naming
        user = User.query.get(user_id)
        if user:
            # Create safe folder name from email (replace special chars)
            safe_email = user.email.replace('@', '_at_').replace('.', '_dot_').replace('-', '_')
            user_dir = os.path.join(app.instance_path, 'users', safe_email)
            os.makedirs(user_dir, exist_ok=True)
            return user_dir
    return None

def get_user_upload_folder(user_id):
    """Get the upload folder path for a specific user"""
    if user_id:
        user_dir = get_user_folder(user_id)
        if user_dir:
            upload_dir = os.path.join(user_dir, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            return upload_dir
    # Fallback to global upload folder for anonymous users
    return app.config['UPLOAD_FOLDER']

def get_user_log_folder(user_id):
    """Get the log folder path for a specific user"""
    if user_id:
        user_dir = get_user_folder(user_id)
        if user_dir:
            log_dir = os.path.join(user_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            return log_dir
    return None
```

#### 2. **Updated Upload Logic**
- File uploads now use `get_user_upload_folder(current_user.id)`
- CSV paste uploads use the same user-specific folder
- File deletion uses user-specific paths

#### 3. **Enhanced Logging**
- User logs go to their specific folder: `users/{safe_email}/logs/user.log`
- Anonymous user logs go to: `logs/notLogged/anonymous.log`
- System logs remain in: `logs/system/system.log`

### Frontend Changes

#### 1. **Dynamic Upload Folder**
- The `/api/config` endpoint now returns user-specific upload folders
- JavaScript automatically uses the correct folder for uploads

#### 2. **Configuration Loading**
- Frontend loads user-specific configuration on page load
- Upload paths are dynamically determined based on user authentication

## Benefits

### 🛡️ **Security**
- **User Isolation**: Each user's files are completely separated
- **Access Control**: Users can only access their own upload folders
- **Audit Trail**: Complete logging of user actions in their specific folder

### 📊 **Organization**
- **Clear Structure**: Easy to locate user-specific data
- **Scalability**: Supports unlimited users without folder conflicts
- **Maintenance**: Easy to clean up or backup individual user data

### 🔍 **Debugging**
- **User-Specific Logs**: Easy to trace issues for specific users
- **File Tracking**: Clear connection between logs and uploaded files
- **Error Isolation**: User errors don't affect other users' logs

## File Naming Convention

### Uploaded Files
```
{dataset_id}_{file_type}_{timestamp}.{extension}
```

**Examples:**
- `1_patients_1234567890.csv`
- `1_taxonomy_1234567891.csv`
- `1_bracken_1234567892.csv`

### Log Files
- **User Logs**: `users/{safe_email}/logs/user.log`
- **Anonymous Logs**: `logs/notLogged/anonymous.log`
- **System Logs**: `logs/system/system.log`

## Migration Notes

### Existing Files
- Existing files in the global `uploads/` folder remain accessible
- New uploads will use user-specific folders
- Old files can be migrated manually if needed

### Database Compatibility
- No database changes required
- File paths in the database remain the same
- Only the physical storage location changes

## Configuration

### Environment Variables
```bash
# Global fallback upload folder (for anonymous users)
UPLOAD_FOLDER=uploads

# Log directory (managed automatically)
# No configuration needed - uses instance/logs/
```

### Automatic Creation
The following directories are created automatically:
- `instance/users/` - User-specific folders
- `instance/users/{safe_email}/` - Individual user folders (created on first login)
- `instance/users/{safe_email}/logs/` - User log folders
- `instance/users/{safe_email}/uploads/` - User upload folders
- `instance/logs/notLogged/` - Anonymous user logs

## Monitoring and Maintenance

### Log Rotation
- User logs: 10MB max, 5 backup files
- System logs: 50MB max, 10 backup files
- Audit logs: 100MB max, 20 backup files

### Cleanup
- User folders can be safely deleted when users are removed
- Log files are automatically rotated to prevent disk space issues
- Upload folders can be cleaned up independently

## Result

✅ **User Isolation**: Each user has their own folder structure  
✅ **Automatic Creation**: Folders are created on-demand  
✅ **Backward Compatibility**: Existing files remain accessible  
✅ **Enhanced Security**: User data is properly separated  
✅ **Better Organization**: Clear structure for logs and uploads  
✅ **Scalable Architecture**: Supports unlimited users  

The new folder structure provides better organization, security, and maintainability while maintaining full backward compatibility with existing functionality.
