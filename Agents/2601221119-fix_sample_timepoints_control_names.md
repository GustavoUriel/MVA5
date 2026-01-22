# 2601221119 - Fix Sample Timepoints Control Names

## Issue Description
In the 'Sample Timepoints Comparison' section of the analysis configuration editor, the checkboxes for timepoint selection were using incorrect name and id attributes. The requirements specified that these should be set to the value of the 'control_name_post_analysis' field from the API response, but they were using prefixed versions like "sample_tp_${control_name_post_analysis}".

## Root Cause
The displaySampleTimepoints function in dataset_analysis.js was setting id and name attributes with a "sample_tp_" prefix instead of using the raw control_name_post_analysis value. Additionally, the updateSampleTimepointsVisibility function was comparing checkbox values (which are control_name_post_analysis) against the select dropdown values (which are tp.value), causing a mismatch in the logic for disabling the currently selected primary timepoint.

## Changes Made

### 1. Updated displaySampleTimepoints Function
- Changed checkbox id from `id="sample_tp_${tp.control_name_post_analysis}"` to `id="${tp.control_name_post_analysis}"`
- Changed checkbox name from `name="sample_tp_${tp.control_name_post_analysis}"` to `name="${tp.control_name_post_analysis}"`
- Changed label for attribute from `for="sample_tp_${tp.control_name_post_analysis}"` to `for="${tp.control_name_post_analysis}"`
- Added storage of timepoints data: `this.sampleTimepointsData = timePoints;`

### 2. Updated updateSampleTimepointsVisibility Function
- Added logic to find the selected timepoint object: `const selectedTp = this.sampleTimepointsData ? this.sampleTimepointsData.find(tp => tp.value === selectedValue) : null;`
- Extracted the control name: `const selectedControlName = selectedTp ? selectedTp.control_name_post_analysis : '';`
- Changed comparison from `if (cb.value === selectedValue)` to `if (cb.value === selectedControlName)`

## Files Modified
- `app/static/js/dataset_analysis.js`: Updated displaySampleTimepoints and updateSampleTimepointsVisibility functions

## Testing
- Verified that checkbox id/name attributes now match the control_name_post_analysis values from the API
- Ensured that the primary selected timepoint checkbox is properly disabled when selected
- Confirmed that the UI layout and functionality remain intact

## Summary
Successfully updated the Sample Timepoints Comparison section to use correct control names for checkbox id and name attributes, ensuring proper form data binding and UI behavior. The changes align with the API specification and maintain existing functionality.