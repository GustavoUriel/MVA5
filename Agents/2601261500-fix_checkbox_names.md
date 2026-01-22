# 2601261500-fix_checkbox_names.md

## Summary
Updated Analysis Methods Comparison section checkbox names and ids to use 'control_name_post_analysis' values from the API instead of 'control_name' values, ensuring consistency with backend expectations for form processing.

## Changes Made

### 1. Updated data processing in loadAnalysisMethods()
- Modified the analysisMethodsData mapping to include `postAnalysisKey: method.control_name_post_analysis`
- This field is now available for use in the UI rendering

### 2. Updated displayAnalysisMethodsComparison() checkbox template
- Changed checkbox `value` attribute from `m.key` to `m.postAnalysisKey`
- Changed checkbox `id` attribute from `analysis_method_${m.key}` to `analysis_method_${m.postAnalysisKey}`
- Changed checkbox `name` attribute from `analysis_method_${m.key}` to `analysis_method_${m.postAnalysisKey}`
- Changed label `for` attribute to match the new id

### 3. Updated updateAnalysisMethodsVisibility() logic
- Modified the disable/uncheck logic to compare checkbox values with the postAnalysisKey of the selected method
- Added lookup to find the selected method's postAnalysisKey from analysisMethodsData
- Changed comparison from `cb.value === selectedValue` to `cb.value === selectedPostAnalysisKey`

## Technical Details
- The collected values in `collectAnalysisMethodsComparison()` now return an array of `control_name_post_analysis` values instead of `control_name` values
- This ensures that the saved configuration contains the post-analysis control names that the backend expects for processing
- The disable/uncheck functionality continues to work correctly by mapping the selected method's control_name to its corresponding postAnalysisKey

## Validation
- Checkbox names and ids now use the post-analysis control names as requested
- Disable/uncheck logic properly prevents selection of the currently chosen analysis method
- Form data collection captures the correct identifiers for backend processing