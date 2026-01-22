# Fix Stratification Display in Population Sectors Comparison UI

## Summary
Updated the `displayStratifications` function in both the global scope and the `DatasetAnalysisManager` class in `app/static/js/dataset_analysis.js` to correctly display stratification subgroups and use `control_name_post_analysis` for checkbox IDs and names.

## Changes Made
1. **Global `displayStratifications` function**:
   - Changed checkbox ID and name from `strat_${index}_${stratification.key}` to `stratification.control_name_post_analysis || strat_${index}_${stratification.key}`
   - Ensured subgroups are rendered as a proper list with name and condition.

2. **DatasetAnalysisManager.displayStratifications method**:
   - Updated to use `strat.control_name_post_analysis` for checkbox IDs and names.
   - Fixed subgroups rendering to display each subgroup's name and condition in a bulleted list.

## Files Modified
- `app/static/js/dataset_analysis.js`

## Validation
- The UI should now properly display stratification subgroups as lists.
- Checkboxes will have names/IDs matching the API's `control_name_post_analysis` field.
- No syntax errors introduced; code follows existing patterns.