# 2601201440-force_control_name_for_checkboxes.md

## Date: 2026-01-20 14:40

### Change
- Updated `displayColumnGroups` in `app/static/js/dataset_analysis.js` to use only the `control_name` field from metadata for both the `id` and `name` of each checkbox, with no fallback. This guarantees exact correspondence with the source metadata.

### Summary
Checkbox controls for attribute groups now use only the `control_name` from the backend for their `id` and `name` attributes, matching the Python source exactly.
