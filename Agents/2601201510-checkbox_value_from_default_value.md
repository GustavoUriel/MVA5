# 2601201510-checkbox_value_from_default_value.md

## Date: 2026-01-20 15:10

### Change
- Updated `displayColumnGroups` in `app/static/js/dataset_analysis.js` so that the `value` of each checkbox is set to the `default_value` field from the backend (if present), not `control_name`. The `id` and `name` remain as `control_name`.

### Summary
Checkbox controls for attribute groups now use the `default_value` from the backend for their `value` attribute, exactly as specified in the source. If `default_value` is missing, the value is set to an empty string.
