# 2601161505-fix_duplicate_route_error.md

## Summary
Fixed AssertionError caused by duplicate route definitions for the bracken-time-points endpoint in the datasets blueprint.

## Problem
The Flask application failed to start with the error:
```
AssertionError: View function mapping is overwriting an existing endpoint function: datasets.get_bracken_time_points
```

## Root Cause
There were two identical route decorators and functions defined for `/dataset/<int:dataset_id>/metadata/bracken-time-points`:

1. **First function** (line 406): Returned data with 'suffix' field
2. **Second function** (line 805): Returned data with 'name' field (correct for JavaScript compatibility)

Both functions had the same route pattern, causing Flask to detect a duplicate endpoint registration.

## Solution
Removed the first duplicate function that returned 'suffix' data, keeping only the second function that returns 'name' data, which is compatible with the JavaScript frontend expectations.

## Technical Details

### Removed Function (First duplicate):
```python
@datasets_bp.route('/dataset/<int:dataset_id>/metadata/bracken-time-points')
@login_required
def get_bracken_time_points(dataset_id):
  # Returned: 'suffix', 'description', 'timepoint', 'function'
```

### Kept Function (Second implementation):
```python
@datasets_bp.route('/dataset/<int:dataset_id>/metadata/bracken-time-points')
@login_required
def get_bracken_time_points(dataset_id):
  # Returns: 'key', 'name', 'description', 'suffix', 'timepoint', 'function'
```

## Impact
- ✅ Flask application now starts successfully
- ✅ Time point selection UI continues to work correctly
- ✅ API returns proper data structure with 'name' field for JavaScript consumption
- ✅ No functionality lost - the correct implementation remains

## Files Modified
1. `app/modules/datasets/datasets_bp.py` - Removed duplicate route function

## Testing
- ✅ Flask app creation: `python -c "from app.app import create_app; app = create_app(); print('Flask app created successfully')"`
- ✅ No duplicate route errors
- ✅ Application starts without AssertionError

## Related Changes
This fix supports the recent TimePoint Selection UI enhancements that require the API to return 'name' fields instead of 'suffix' fields for proper JavaScript integration.</content>
<parameter name="filePath">c:\code\Rena Python\MVA5\2601161505-fix_duplicate_route_error.md