# 2601201410-attribute_group_controls_control_name.md

## Date: 2026-01-20 14:10

### Change
- Updated `displayColumnGroups` in `app/static/js/dataset_analysis.js` so that each checkbox's `id` and `name` are set to the group's `control_name` (from backend, matching `COLUMN_GROUPS.py`).
- This ensures the controls for each attribute group are named and identified exactly as in the source metadata.

### Summary
All attribute group checkboxes in the analysis UI now use the `control_name` from the backend for their `id` and `name` attributes, matching the Python source. This enables precise mapping and downstream processing.
