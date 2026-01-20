# 2601201450-checkbox_id_name_control_name_only.md

## Date: 2026-01-20 14:50

### Change
- Updated `displayColumnGroups` in `app/static/js/dataset_analysis.js` so that the `id`, `name`, and `value` of each checkbox are set to the `control_name` field from the source metadata, with no fallback to `name` or any other field.

### Summary
Checkbox controls for attribute groups now use only the `control_name` from the backend for their `id`, `name`, and `value` attributes, exactly matching the Python source.
