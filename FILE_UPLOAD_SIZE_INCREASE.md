# File Upload Size Limit Increase - 100MB Support

## Problem Identified

The application was limiting file uploads to **16MB**, which was insufficient for large bracken results files that can exceed **20MB**. Users were unable to upload their microbiome analysis data.

## Solution Applied

### 1. Updated Application Configuration

**File**: `app.py`
- **Line 37**: Changed default `MAX_CONTENT_LENGTH` from 16MB to 100MB
- **Before**: `16 * 1024 * 1024` (16,777,216 bytes)
- **After**: `100 * 1024 * 1024` (104,857,600 bytes)

### 2. Updated Environment Configuration

**File**: `.env`
- **Line 25**: Updated `MAX_CONTENT_LENGTH` from 16MB to 100MB
- **Before**: `MAX_CONTENT_LENGTH=16777216`
- **After**: `MAX_CONTENT_LENGTH=104857600`

**File**: `env.template`
- Updated template to reflect new default of 100MB
- **Before**: `MAX_CONTENT_LENGTH=16777216`
- **After**: `MAX_CONTENT_LENGTH=104857600`

### 3. Enhanced Error Handling

**File**: `app.py` - Error Handler (413)
- **Improved error message**: Now shows exact file size limit
- **Better logging**: Includes max size in MB for easier debugging
- **User-friendly**: Clear message about maximum allowed file size

## Technical Details

### File Size Limits

| Configuration | Before | After | Change |
|---------------|--------|-------|--------|
| **Default Limit** | 16MB | 100MB | +84MB |
| **Bytes** | 16,777,216 | 104,857,600 | +88,080,384 |
| **Environment Variable** | `16777216` | `104857600` | Updated |

### Supported File Types

The increased limit applies to all supported file types:
- **CSV files** (patients, taxonomy, bracken results)
- **TSV files** (tab-separated values)
- **TXT files** (text files)

### Upload Methods

Both upload methods now support 100MB files:
- **File Upload**: Direct file selection
- **CSV Paste**: Large CSV content pasting

## Verification

### Configuration Test
```bash
python -c "from app import app; print('Max upload size:', app.config['MAX_CONTENT_LENGTH'] // (1024*1024), 'MB')"
# Output: Max upload size: 100 MB
```

### Environment Variable Check
```bash
Get-Content ".env" | Select-String "MAX_CONTENT_LENGTH"
# Output: MAX_CONTENT_LENGTH=104857600
```

## Benefits

### For Users
- ✅ **Large file support**: Upload bracken results files up to 100MB
- ✅ **Better error messages**: Clear indication of file size limits
- ✅ **No upload failures**: Eliminates 413 errors for files under 100MB

### For System
- ✅ **Flexible configuration**: Easy to adjust via environment variables
- ✅ **Improved logging**: Better error tracking and debugging
- ✅ **Backward compatibility**: Existing smaller files still work

## Considerations

### Performance Impact
- **Memory usage**: Larger files require more server memory
- **Upload time**: 100MB files will take longer to upload
- **Storage**: Ensure sufficient disk space for large files

### Server Configuration
- **Web server limits**: May need to adjust nginx/apache limits
- **Timeout settings**: Consider increasing upload timeouts
- **Memory allocation**: Ensure adequate memory for file processing

## Usage

### For Bracken Results Files
1. **File size**: Can now upload files up to 100MB
2. **Format**: CSV, TSV, or TXT format
3. **Content**: Bracken abundance estimation results
4. **Upload method**: File upload or CSV paste

### Error Handling
If a file exceeds 100MB, users will see:
```
File too large. Maximum file size is 100MB.
```

## Next Steps

The application now supports large bracken results files. Users can:
- ✅ Upload files up to 100MB
- ✅ Use both file upload and CSV paste methods
- ✅ Receive clear error messages for oversized files
- ✅ Process large microbiome datasets

The file upload system is now ready for large-scale microbiome analysis data.
