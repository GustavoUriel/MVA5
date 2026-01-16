# Bracken Time Point Combobox Improvements - 2601161843

## Summary
Updated the Bracken Time Point Selection combobox to display only titles from metadata and show full descriptions, with improved layout (1/3 combobox, 2/3 description).

## Changes Made

### 1. HTML Layout Update (app/templates/dataset/analysis_config.html)
- **File:** `app/templates/dataset/analysis_config.html`
- **Line:** 188-205
- **Change:** Modified Bootstrap column classes from `col-md-8` (combobox) and `col-md-4` (description) to `col-md-4` (combobox) and `col-md-8` (description)
- **Purpose:** Resize combobox to 1/3 width and description to 2/3 width as requested

### 2. JavaScript Dropdown Display (app/static/js/dataset.js)
- **Function:** `displayBrackenTimePoints()`
- **Lines:** 1059-1088
- **Changes:**
  - Added global storage for descriptions: `window.brackenTimePointDescriptions = {}`
  - Changed dropdown text from `${formatTimePointName(timePoint.key)} - ${timePoint.description}` to `timePoint.title`
  - Added `data-description` attribute to options for backward compatibility
  - Store descriptions in global object for access by description update function

### 3. JavaScript Description Update (app/static/js/dataset.js)
- **Function:** `updateTimePointDescription()`
- **Lines:** 2011-2036
- **Changes:**
  - Simplified function to use actual description from metadata
  - Access stored descriptions from `window.brackenTimePointDescriptions`
  - Display the full description text directly instead of building custom text
  - Fixed element ID reference from `timePointDescription` to `timePointDescriptionText`

## Technical Details
- **Data Source:** Uses existing API endpoint `/dataset/<int:dataset_id>/metadata/bracken-time-points`
- **Metadata File:** `metadata/BRACKEN_TIME_POINTS.py` provides title and description fields
- **Layout:** Bootstrap grid system with responsive columns (col-md-4 for combobox, col-md-8 for description)
- **JavaScript:** Global object storage for efficient description access on combobox changes

## Verification
- No linting errors introduced
- Maintains backward compatibility with existing data attributes
- Preserves existing functionality while improving user experience

## Summary
Successfully implemented the requested improvements to the Bracken Time Point Selection combobox, making it more user-friendly with cleaner display and better layout.