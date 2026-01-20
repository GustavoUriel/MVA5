# 2601200003-add_default_value_column_groups.md

## Change Summary

- Added a `default_value` attribute to each group in `COLUMN_GROUPS` in metadata/COLUMN_GROUPS.py, with the value set to True.

## Reason

- To provide a `default_value` field for each group, as requested, possibly for use in UI or logic defaults.

## Files Modified

- metadata/COLUMN_GROUPS.py

## Details

- For each dictionary entry in `COLUMN_GROUPS`, a new key `default_value` was added, with its value set to True. Indentation and structure were verified for correctness.

---

### Summary
Added `default_value: True` to all groups in COLUMN_GROUPS. No other logic or structure was changed.