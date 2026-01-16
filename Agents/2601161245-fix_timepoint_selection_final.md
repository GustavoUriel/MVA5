# 2601161245-fix_timepoint_selection_final.md

## Changes Made

### Modified `displayBrackenTimePoints` function in `app/static/js/dataset_analysis.js`
- Removed auto-selection of the first time point on page load
- The dropdown now starts with the placeholder "Select time point..." option

### Modified `updateTimePointDescription` function in `app/static/js/dataset_analysis.js`
- Changed initial description text to "Select the Time Point of the Bracken count"
- Added logic to remove the placeholder option after first selection, preventing users from selecting it again
- When a time point is selected, the description shows the formatted time point name

## Summary
Fixed the Bracken Time Point Selection card to start with a placeholder option, display the correct initial description text, and prevent re-selection of the placeholder after a time point has been chosen, while properly updating the description with the selected time point name.