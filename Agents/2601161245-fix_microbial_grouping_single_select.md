# 2601161245-fix_microbial_grouping_single_select.md

## Summary
Fixed microbial grouping functionality to enforce single selection instead of multi-selection. Changed UI from checkboxes to radio buttons and updated all related JavaScript logic.

## Changes Made

### Backend API (app/modules/datasets/datasets_bp.py)
- Added new endpoint `/dataset/{datasetId}/metadata/microbial-grouping` to load microbial grouping methods
- Follows same pattern as other metadata endpoints
- Returns ordered list of grouping methods with their configurations

### Frontend JavaScript (app/static/js/dataset_analysis.js)
- **displayMicrobialGroupingPolicies()**: Changed input type from checkbox to radio button with shared name "microbialGroupingMethod"
- **collectMicrobialGrouping()**: Rewritten to return single selected method object instead of array of enabled methods
- **updateMicrobialGroupingSummary()**: Updated to handle radio button selection, showing selected method name
- **toggleMicrobialGroupingBody()**: Modified to hide all method bodies first, then show only the selected method's body
- **resetAnalysisEditor()**: Added updateMicrobialGroupingSummary() call to reset summaries section

## Technical Details
- Radio buttons ensure only one microbial grouping method can be selected at a time
- Method parameter forms toggle visibility based on selection
- Summary text updates dynamically to show selected method
- Reset functionality properly clears radio selection and hides all parameter forms

## Validation
- API endpoint returns proper JSON response with grouping methods
- UI now enforces single selection behavior
- Parameter forms show/hide correctly based on selection
- Summary updates properly on selection changes and reset

## Impact
- Users can now only select one microbial grouping method per analysis configuration
- Eliminates potential confusion from multi-selection interface
- Maintains consistency with other single-choice configuration sections