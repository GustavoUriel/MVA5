# 2601201620-disable-selected-method-in-comparison.md

## Date/Time
2026-01-20 16:20

## Change Summary
- Modified `updateAnalysisMethod()` in `dataset_analysis.js` to call `this.updateAnalysisMethodsVisibility()` after toggling parameter containers.
- This ensures that when the Analysis Method dropdown selection changes, the corresponding method in the "Analysis Methods Comparison" section is disabled (checkbox unchecked and disabled, label muted).
- Removed the old try-catch block that attempted to call `window.analysisManager.updateAnalysisMethodsVisibility()`.

## Files Modified
- `app/static/js/dataset_analysis.js`

## Reason
- To disable the currently selected analysis method in the comparison list, preventing users from selecting the same method for both primary analysis and comparison.

## Final Summary
This update ensures that the selected method in the Analysis tab dropdown is properly disabled in the Analysis Methods Comparison section, maintaining UI consistency and preventing duplicate selections. All changes are logged here for traceability.
