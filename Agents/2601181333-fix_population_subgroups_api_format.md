# 2601181333-fix_population_subgroups_api_format.md

## Summary
Updated the backend API endpoint `/dataset/{id}/metadata/stratifications` to properly format POPULATION_SUBGROUPS data for frontend consumption. The endpoint now loads POPULATION_SUBGROUPS instead of STRATIFICATIONS and formats each population subgroup as a group containing a single stratification, matching the expected frontend structure.

## Changes Made

### Backend API Update
- **File:** `app/modules/datasets/datasets_bp.py`
- **Function:** `get_stratifications()`
- **Change:** Modified to load `POPULATION_SUBGROUPS` metadata module instead of `STRATIFICATIONS`
- **Formatting:** Each population subgroup is now formatted as a group with a single stratification containing the subgroup's parameters, description, and info

### Data Structure
The API now returns:
```json
{
  "success": true,
  "stratifications": [
    {
      "group_name": "demographics",
      "group_label": "Demographics Analysis",
      "stratifications": [
        {
          "name": "demographics",
          "label": "Demographics Analysis",
          "type": "population_subgroup",
          "method": "direct",
          "groups": [],
          "parameters": {...},
          "description": "...",
          "info": {...}
        }
      ]
    }
  ]
}
```

## Testing
- Verified the API endpoint loads POPULATION_SUBGROUPS metadata correctly
- Confirmed the response format matches frontend expectations
- Population Sectors Comparison section should now display the 7 grouping strategies with their parameters and descriptions

## Files Affected
- `app/modules/datasets/datasets_bp.py` - Updated get_stratifications endpoint
- `metadata/POPULATION_SUBGROUPS.py` - Provides the data source (created previously)

## Next Steps
- Test the UI integration by running the application and verifying Population Sectors Comparison section loads correctly
- Ensure parameter forms display properly for each grouping strategy
- Verify that selected groupings are properly saved in analysis configurations