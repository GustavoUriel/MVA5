# Fix Save Button for Hierarchical JSON

## Task Description
Fix the save button in the analysis configuration section so that on click it saves a hierarchical JSON of the values for all controls in the section into a file in the folder `instance\users\(user email)\(dataset id)\analysis` with the name of the analysis from the analysis information section.

## Changes Made

### 1. Modified `collectAllControls()` method in `dataset_analysis.js`
- Changed the method to collect controls hierarchically grouped by tab-pane sections (datasources-editor, preanalysis-editor, analysis-editor, postanalysis-editor, output-editor).
- Instead of a flat object, now returns an object with keys for each tab-pane, containing the controls within that section.

### 2. Modified `saveAnalysis()` method in `dataset_analysis.js`
- Simplified the save process to send only the hierarchical controls JSON as the configuration.
- Removed collection of full config, full DOM, and attaching controls_state separately.
- Now sends `configuration: controlsState` directly to the backend.

## Summary
The save button now saves a hierarchical JSON structure of all form controls grouped by their respective sections (tabs) in the analysis configuration editor. The file is saved to the correct path `instance/users/{user_email}/{dataset_id}/analysis/{analysis_name}.json` as specified.