# 2601202204-modify_metadata_endpoints_to_return_arrays.md

## Summary
Modified the first three metadata endpoints to return arrays with all data from source files, ready for frontend consumption:

1. `/dataset/<int:dataset_id>/metadata/bracken-time-points` - Now returns `bracken_time_points` array with all BRACKEN_TIME_POINTS data
2. `/dataset/<int:dataset_id>/metadata/column-groups` - Now returns `column_groups` array with all COLUMN_GROUPS data  
3. `/dataset/<int:dataset_id>/metadata/attribute-discarding` - Now returns `attribute_discarding_policies` array with all ATTRIBUTE_DISCARDING data

## Changes Made

### 1. Bracken Time Points Endpoint
- **File:** `app/modules/datasets/datasets_bp.py`
- **Function:** `get_bracken_time_points()`
- **Change:** Simplified the endpoint to return all BRACKEN_TIME_POINTS data as an array, removing complex file parsing logic
- **Response:** Now returns `bracken_time_points` array with each item containing all fields from the metadata plus a `key` field

### 2. Column Groups Endpoint  
- **File:** `app/modules/datasets/datasets_bp.py`
- **Function:** `get_column_groups()`
- **Change:** Streamlined to return all COLUMN_GROUPS data as an array
- **Response:** Returns `column_groups` array with each item containing all fields from the metadata plus a `group_key` field

### 3. Attribute Discarding Endpoint
- **File:** `app/modules/datasets/datasets_bp.py` 
- **Function:** `get_attribute_discarding_policies()`
- **Change:** Modified to return all ATTRIBUTE_DISCARDING data as an array instead of the original object
- **Response:** Returns `attribute_discarding_policies` array with each item containing all fields from the metadata plus a `policy_key` field

## Technical Details
- All endpoints now return arrays containing complete metadata objects from their respective source files
- Each array item includes the original key as an additional field (e.g., `key`, `group_key`, `policy_key`)
- Frontend can now directly iterate over these arrays without additional transformation
- Maintained backward compatibility by keeping the same endpoint URLs and success/error response structure

## Files Modified
- `app/modules/datasets/datasets_bp.py` - Updated three endpoint functions

## Testing
- Endpoints should return arrays ready for frontend consumption
- All original data from metadata files is preserved
- Response format is consistent across endpoints