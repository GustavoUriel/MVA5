# 2601201430-fix_column_group_checkbox_naming.md

## Date: 2026-01-20 14:30

### Change
- Updated `displayColumnGroups` in `app/static/js/dataset_analysis.js` to ensure each checkbox's `id` and `name` are set to the group's `control_name` (falling back to `group_key` if missing), matching the metadata exactly.

### Summary
Checkbox controls for attribute groups are now named and identified exactly as specified in the source metadata, ensuring correct mapping and downstream processing.
