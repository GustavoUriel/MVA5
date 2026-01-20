# 2601201550-fix_analysis_method_global_function.md

## Date/Time
2026-01-20 15:50

## Change Summary
- Added a global `window.updateAnalysisMethod` function in `dataset_analysis.js` that calls the manager's `updateAnalysisMethod()` method.
- This allows the HTML `onchange="updateAnalysisMethod()"` to call the new visibility-only function instead of the old fetch-based one in `dataset.js`.
- The new function only toggles parameter container visibility and does not perform any network requests.

## Files Modified
- `app/static/js/dataset_analysis.js`

## Reason
- To ensure that changing the Analysis Method dropdown only toggles visibility of pre-created parameter containers, without triggering any fetches or errors.

## Final Summary
This update ensures the dropdown change event calls the correct function, preventing TypeErrors and unwanted fetches. All changes are logged here for traceability.
