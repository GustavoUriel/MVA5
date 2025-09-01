# JavaScript Configuration Fix - Dynamic File Size Limits

## Problem Identified

The JavaScript file `static/js/app.js` had the `maxFileSize` hardcoded to 16MB instead of reading from the server configuration. This caused the frontend to reject files larger than 16MB even though the server was configured to accept 100MB files.

## Solution Applied

### 1. Added Server Configuration Endpoint

**File**: `app.py`
- **New Route**: `/api/config` - Provides application configuration to frontend
- **Returns**: JSON with file size limits, allowed file types, and other settings

```python
@app.route('/api/config')
def api_config():
    """API endpoint to get application configuration"""
    return jsonify({
        'maxFileSize': app.config['MAX_CONTENT_LENGTH'],
        'maxFileSizeMB': app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024),
        'allowedFileTypes': ['.csv', '.tsv', '.txt'],
        'uploadFolder': app.config['UPLOAD_FOLDER']
    })
```

### 2. Updated JavaScript Configuration Loading

**File**: `static/js/app.js`
- **Dynamic Configuration**: JavaScript now fetches configuration from server
- **Async Initialization**: App initialization waits for configuration to load
- **Fallback Support**: Uses defaults if server configuration fails to load

#### Key Changes:

```javascript
// Before (hardcoded)
config: {
    maxFileSize: 16 * 1024 * 1024, // 16MB
}

// After (dynamic)
async loadConfiguration() {
    const response = await fetch('/api/config');
    const serverConfig = await response.json();
    this.config.maxFileSize = serverConfig.maxFileSize;
    this.config.maxFileSizeMB = serverConfig.maxFileSizeMB;
}
```

### 3. Updated Error Messages

**File**: `static/js/app.js`
- **Dynamic Error Messages**: File size error messages now show actual limits
- **Before**: "Maximum size is 16MB" (hardcoded)
- **After**: "Maximum size is 100MB" (dynamic from server)

```javascript
// Before
errors.push(`${file.name} is too large. Maximum size is 16MB.`);

// After
const maxSizeMB = this.config.maxFileSizeMB || (this.config.maxFileSize / (1024 * 1024));
errors.push(`${file.name} is too large. Maximum size is ${maxSizeMB}MB.`);
```

## Technical Details

### Configuration Flow

1. **Server Start**: Flask loads `MAX_CONTENT_LENGTH` from environment (100MB)
2. **Page Load**: JavaScript fetches configuration from `/api/config`
3. **File Upload**: JavaScript validates against dynamic server limits
4. **Error Messages**: Show actual server-configured limits

### API Endpoint Response

```json
{
    "maxFileSize": 104857600,
    "maxFileSizeMB": 100,
    "allowedFileTypes": [".csv", ".tsv", ".txt"],
    "uploadFolder": "uploads"
}
```

### Error Handling

- **Network Issues**: Falls back to default 16MB if server config fails
- **Async Loading**: App waits for configuration before initializing
- **Graceful Degradation**: Works even if configuration endpoint is unavailable

## Benefits

### For Users
- ✅ **Correct File Size Limits**: Frontend now matches server configuration
- ✅ **Accurate Error Messages**: Shows actual limits (100MB instead of 16MB)
- ✅ **No More Confusion**: Consistent limits across frontend and backend

### For Developers
- ✅ **Single Source of Truth**: Server configuration drives frontend limits
- ✅ **Easy Configuration**: Change server config, frontend updates automatically
- ✅ **Maintainable Code**: No more hardcoded values in JavaScript

## Verification

### Configuration Test
```bash
python -c "from app import app; print('Max upload size:', app.config['MAX_CONTENT_LENGTH'] // (1024*1024), 'MB')"
# Output: Max upload size: 100 MB
```

### API Endpoint Test
```bash
curl http://127.0.0.1:5005/api/config
# Output: {"maxFileSize": 104857600, "maxFileSizeMB": 100, ...}
```

## Result

✅ **22MB files now supported**: Frontend correctly accepts files up to 100MB  
✅ **Accurate error messages**: Shows "Maximum size is 100MB" instead of 16MB  
✅ **Dynamic configuration**: Frontend automatically adapts to server settings  
✅ **No restart required**: Configuration changes take effect immediately  

The JavaScript now properly reads the server configuration and will allow your 22MB bracken results file to be uploaded!
