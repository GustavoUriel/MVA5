# 2601211307 - Unify extremeTimePointSummaryText handling

## Summary
Completed the unification of extremeTimePointSummaryText control handling by consolidating functionality from dataset.js into dataset_analysis.js and updating all references.

## Changes Made

### dataset_analysis.js
- **Enhanced updateExtremeTimePointSummary method**: Moved comprehensive logic from dataset.js including API calls for patient count retrieval, selection mode handling (value-based vs patient-based), and fallback mechanisms
- **Removed duplicate functions**: Eliminated loadPatientCount and updatePatientCounts methods that were redundant with the unified implementation
- **Updated updateExtremeTimePointSummaryFallback**: Simplified to use the main method with fallback logic

### dataset.js
- **Removed duplicate functions**: Deleted updateExtremeTimePointSummary, updateExtremeTimePointSummaryFallback, and loadPatientCount functions
- **Updated function calls**: Changed all remaining updateExtremeTimePointSummary() calls to use window.analysisManager.updateExtremeTimePointSummary()
  - updateTopPercentage function (line ~2291)
  - updateBottomPercentage function (line ~2314)
  - validateAnalysisEditor function (lines ~2741, ~2743)

## Technical Details
- **API Integration**: The unified method uses DatasetUtils.api to fetch patient counts from `/dataset/${datasetId}/patient-counts` endpoint
- **Selection Mode Support**: Handles both value-based and patient-based selection modes with appropriate summary text generation
- **Error Handling**: Includes proper error handling with fallback to default text when API calls fail
- **DOM Updates**: Updates both the summary text element and patient count badges consistently

## Validation
- All function calls now reference the unified analysisManager method
- No remaining global updateExtremeTimePointSummary functions in dataset.js
- Code is consolidated in DatasetAnalysisManager class for better organization

## Summary
Successfully unified the extremeTimePointSummaryText handling by moving all logic to dataset_analysis.js DatasetAnalysisManager class and updating all references. This eliminates code duplication and ensures consistent behavior across the analysis editor.