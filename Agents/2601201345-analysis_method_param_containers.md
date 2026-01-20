# 2601201345-analysis_method_param_containers.md

## Change Summary

- Refactored the Analysis Type section in the analysis editor to pre-create a container for each analysis method's parameters (one per method), using the method's key for the container id.
- Updated the JavaScript to generate all parameter controls for all methods at load time, using the `control_name` field for id/name of each control.
- Instead of dynamically creating/destroying controls, the UI now shows/hides the relevant method's parameter container when the user selects a method in the combobox, hiding all others.
- HTML and JS changes are least invasive and follow project conventions.

## Files Modified
- app/templates/dataset/analysis_config.html
- app/static/js/dataset_analysis.js

## Summary

The Analysis Type section now has a dedicated container for each method's parameters, all controls are present in the DOM, and only the selected method's parameters are visible. This improves performance and maintainability, and ensures all controls use the correct id/name from the API metadata.
