# 2601201630-fix-global-function-reference.md

## Date/Time
2026-01-20 16:30

## Change Summary
- Fixed the global `window.updateAnalysisMethod` function to reference `window.analysisManager` instead of `window.datasetAnalysisManager`.
- This ensures that the HTML onchange event properly calls the manager's `updateAnalysisMethod()`, which in turn calls `updateAnalysisMethodsVisibility()` to disable the selected method in the comparison section.

## Files Modified
- `app/static/js/dataset_analysis.js`

## Reason
- The DatasetAnalysisManager instance is stored as `window.analysisManager`, not `window.datasetAnalysisManager`, so the global function was not finding the manager.

## Final Summary
This fix ensures that changing the analysis method dropdown correctly disables the corresponding method in the comparison list. All changes are logged here for traceability.
