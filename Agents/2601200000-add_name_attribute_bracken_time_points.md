# 2601200000-add_name_attribute_bracken_time_points.md

## Change Summary

- Added a `name` attribute to each time point in `BRACKEN_TIME_POINTS` in metadata/BRACKEN_TIME_POINTS.py. The value of `name` is identical to the value of `title` for each entry.

## Reason

- To provide a direct `name` field for each time point, as requested, possibly for easier or more consistent access in code or UI.

## Files Modified

- metadata/BRACKEN_TIME_POINTS.py

## Details

- For each dictionary entry in `BRACKEN_TIME_POINTS`, a new key `name` was added, with its value set to the same as the `title` value for that entry.

---

### Summary
Added a `name` attribute to all time points in BRACKEN_TIME_POINTS, duplicating the value of `title` for each. No other logic or structure was changed.