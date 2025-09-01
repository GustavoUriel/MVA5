# Real-Time Statistics Update Fix

## Problem Identified

The file count and total size statistics were not updating in real-time after file uploads. The issue was in the backend where the file count was being calculated before the new file was committed to the database.

## Root Cause

In the upload function (`upload_dataset_file`), the file count was calculated using:
```python
dataset.file_count = len(dataset.files)
```

However, this was happening **before** the new file was committed to the database, so `len(dataset.files)` didn't include the newly uploaded file.

## Solution Applied

### 1. Fixed Backend File Count Calculation

**File**: `app.py`
- **Problem**: File count calculated before database commit
- **Solution**: Calculate file count after commit and refresh

```python
# Before (incorrect)
dataset.file_count = len(dataset.files)  # Before commit
db.session.commit()

# After (correct)
db.session.commit()
db.session.refresh(dataset)  # Refresh to get new file
dataset.file_count = len(dataset.files)  # After commit
dataset.total_size = sum(f.file_size for f in dataset.files)
db.session.commit()
```

### 2. Enhanced Frontend Debugging

**File**: `templates/dataset.html`
- **Added**: Console logging to track updates
- **Added**: Small delay before refreshing files list
- **Added**: Better error handling

```javascript
// Added debugging
console.log('Upload successful, dataset status:', data.dataset_status);
console.log('Updating statistics cards with:', datasetStatus);

// Added delay for database sync
setTimeout(() => {
    loadFiles(); // Refresh files table
}, 500);
```

## Technical Details

### Database Transaction Flow

1. **Save File**: New file saved to database
2. **Update Status**: File type flags updated (patients/taxonomy/bracken)
3. **First Commit**: Commit file and status changes
4. **Refresh Dataset**: Reload dataset with new file
5. **Calculate Statistics**: Count files and calculate total size
6. **Second Commit**: Save updated statistics

### Frontend Update Flow

1. **Upload Request**: Send file to server
2. **Server Response**: Receive updated dataset status
3. **Immediate Update**: Update progress bar and statistics cards
4. **Delayed Refresh**: Wait 500ms, then refresh files table
5. **Visual Feedback**: Show loading states and animations

## Verification

### Test Script
Created `test_file_count.py` to verify:
- File count matches actual files
- Total size calculation is correct
- API endpoints return consistent data

### Console Logging
Added debugging to track:
- Upload response data
- Statistics card updates
- File count and size changes

## Result

✅ **Real-time updates working**: Statistics update immediately after upload  
✅ **Accurate file count**: File count matches actual uploaded files  
✅ **Correct total size**: Total size includes all uploaded files  
✅ **Smooth user experience**: No page refresh needed  

The file count, total size, and uploaded files list now update properly after each file upload!
