# 2601221135-fix_stratification_reset_override.md

## Summary
Modified the DatasetAnalysisManager.resetAnalysisEditor method to exclude stratification checkboxes from being forced to checked state during reset. This allows stratification checkboxes to preserve their 'default' field values from the metadata instead of being overridden.

## Changes Made
- Updated the checkbox selector in resetAnalysisEditor to only target '#columnGroupsContainer input[type="checkbox"]', removing '#stratificationContainer input[type="checkbox"]'
- This preserves the conditional checked attribute set in displayStratifications based on stratification.default values

## Files Modified
- app/static/js/dataset_analysis.js (lines ~1940-1945)

## Testing
- Start Flask app and verify stratification checkboxes now load with their default states from metadata rather than all checked