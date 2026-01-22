# Fix Stratification Cards Layout to Two Columns

## Summary
Updated the stratification cards layout to display in two columns, matching the Analysis Methods Comparison section. Changed the container to use CSS Grid layout and updated the card HTML structure to use `col mb-2` classes instead of Bootstrap responsive columns.

## Changes Made
1. **HTML Template** (`app/templates/dataset/analysis_config.html`):
   - Added `grid-template-columns: repeat(2, 1fr); gap: .5rem;` style to `stratificationContainer` div.

2. **JavaScript Functions** (`app/static/js/dataset_analysis.js`):
   - Updated global `displayStratifications` function to use `<div class="col mb-2">` instead of `<div class="col-md-6 col-lg-4 mb-3">` and removed the `<div class="row">` wrapper.
   - Updated `DatasetAnalysisManager.displayStratifications` method to use `<div class="col mb-2">` instead of `<div class="col-md-6 col-lg-4 mb-3">`.

## Files Modified
- `app/templates/dataset/analysis_config.html`
- `app/static/js/dataset_analysis.js`

## Validation
- The stratification cards now display in a two-column grid layout, consistent with the Analysis Methods Comparison section.
- Cards maintain proper spacing and responsive behavior.
- No syntax errors introduced; layout matches the existing pattern used elsewhere in the application.