# 2601200001-add_name_and_control_name_column_groups.md

## Change Summary

- Added a `name` attribute to each group in `COLUMN_GROUPS` in metadata/COLUMN_GROUPS.py, with the value set to the group's `title`.
- Added a `control_name` attribute to each group, with the value 'AttrGroup_' plus the group's name.

## Reason

- To provide explicit `name` and `control_name` fields for each group, likely for easier or more consistent access in code or UI.

## Files Modified

- metadata/COLUMN_GROUPS.py

## Details

- For each dictionary entry in `COLUMN_GROUPS`, a new key `name` was added, with its value set to the same as the `title` value for that entry.
- For each dictionary entry, a new key `control_name` was added, with its value set to 'AttrGroup_' plus the `name` value.

---

### Summary
Added `name` and `control_name` attributes to all groups in COLUMN_GROUPS. No other logic or structure was changed.