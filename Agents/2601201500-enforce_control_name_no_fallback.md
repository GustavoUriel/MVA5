# 2601201500-enforce_control_name_no_fallback.md

## Date: 2026-01-20 15:00

### Change
- Updated `displayColumnGroups` in `app/static/js/dataset_analysis.js` to use only the `control_name` from the backend for the id, name, and value of each checkbox, with no fallback to any other field. This allows spaces and special characters, matching the source exactly.

### Summary
Checkbox controls for attribute groups now use the exact `control_name` from the backend for their id, name, and value, even if it contains spaces or special characters, ensuring a perfect match to the Python source.
