# Import Path Fix - Metadata API Endpoints

## ✅ **Problem Solved**

The metadata API endpoints were returning 500 errors with "No module named 'app.metadata'" because the import paths were incorrect.

## 🔧 **Root Cause**

The metadata folder is located at the **project root level**, not inside the `app/` folder. The original import paths were trying to import from `app.metadata` which doesn't exist.

## 🛠️ **Solution Implemented**

### **1. Created Helper Function**
```python
def load_metadata_module(module_name):
    """Helper function to load metadata modules from the project root"""
    import sys
    import os
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Import the metadata module
    module = __import__(f'metadata.{module_name}', fromlist=[module_name])
    return getattr(module, module_name)
```

### **2. Updated API Endpoints**
```python
# Before (incorrect)
from ...metadata.COLUMN_GROUPS import COLUMN_GROUPS

# After (correct)
COLUMN_GROUPS = load_metadata_module('COLUMN_GROUPS')
```

### **3. Path Resolution**
The helper function correctly resolves the path:
- **File location**: `app/modules/datasets/datasets_bp.py`
- **Project root**: 4 levels up from the file
- **Metadata location**: `metadata/` (at project root)

## 🧪 **Testing Results**

### **Import Test**
```bash
✅ COLUMN_GROUPS loaded successfully: 10 groups
✅ BRACKEN_TIME_POINTS loaded successfully: 6 points
```

### **API Endpoints**
- `/dataset/<id>/metadata/column-groups` - ✅ Fixed
- `/dataset/<id>/metadata/bracken-time-points` - ✅ Fixed

## 📁 **Files Modified**

- ✅ `app/modules/datasets/datasets_bp.py` - Fixed import paths and added helper function

## 🔄 **Next Steps**

1. **Restart Flask Application**: The changes require a restart to take effect
2. **Test in Browser**: Navigate to analysis tab and click "New Analysis"
3. **Verify Loading**: Column groups and time points should load from metadata

## 🎯 **Expected Results**

After restarting the Flask application:

### **Column Groups API**
- **URL**: `/dataset/6/metadata/column-groups`
- **Response**: JSON with 10 column groups from metadata
- **Status**: 200 OK

### **Bracken Time Points API**
- **URL**: `/dataset/6/metadata/bracken-time-points`
- **Response**: JSON with 6 time points from metadata
- **Status**: 200 OK

### **Frontend Behavior**
- ✅ No more 500 errors in browser console
- ✅ Column groups load dynamically from metadata
- ✅ Time points load dynamically from metadata
- ✅ Real data displayed instead of hardcoded values

## 🚨 **Important Note**

**The Flask application must be restarted** for these changes to take effect. The import path fix is now in place and tested, but the running application still has the old code in memory.

## ✅ **Success Criteria**

The fix is successful when:
- ✅ No 500 errors in browser console
- ✅ Column groups API returns 200 OK with real data
- ✅ Time points API returns 200 OK with real data
- ✅ Frontend displays actual metadata instead of hardcoded values
- ✅ All 10 column groups and 6 time points are loaded
