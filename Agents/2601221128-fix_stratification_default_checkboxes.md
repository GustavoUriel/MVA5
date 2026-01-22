# 2601221128 - Fix Stratification Default Checkboxes

## Summary
Fixed stratification checkboxes to be pre-checked based on the 'default' field from the API response, ensuring that stratifications marked as default are selected by default in the UI.

## Changes Made

### 1. Updated DatasetAnalysisManager.displayStratifications method
- Modified checkbox input to include conditional `checked` attribute: `${strat.default ? 'checked' : ''}`
- Changed `value` attribute from `${strat.default || ''}` to `${controlName}` for proper form submission

### 2. Updated global displayStratifications function
- Applied the same checkbox fixes: conditional `checked` attribute and proper `value` attribute
- Removed the code that explicitly unchecked all stratification checkboxes on load, which was overriding the default selections

## Technical Details
- The 'default' field in stratification metadata is a boolean indicating whether the stratification should be selected by default
- HTML checkboxes are checked using the `checked` attribute, not the `value` attribute
- The `value` attribute should contain the identifier for form submission
- Both class and global versions of the display function needed to be updated for consistency

## Files Modified
- `app/static/js/dataset_analysis.js`: Updated both displayStratifications implementations

## Testing
- Stratification checkboxes should now be pre-checked based on their 'default' field values
- The two-column grid layout should be maintained
- Form submission should include the correct stratification identifiers