# 2601200000-add_control_name_to_attribute_discarding.md

## Change Summary
Added `control_name` to each parameter in every method in [metadata/ATTRIBUTE_DISCARDING.py](metadata/ATTRIBUTE_DISCARDING.py). The value is constructed as param_prefix + parameter key, matching the convention used in ANALYSIS_METHODS.py.

### Details
- Each parameter dictionary now includes a `control_name` field.
- No other logic or structure was changed.

### Example
For `prevalence_filtering`:
- `detection_threshold` → `control_name: 'AtDi_Preval_detection_threshold'`
- `min_prevalence` → `control_name: 'AtDi_Preval_min_prevalence'`

...applied similarly for all other methods and parameters.

---
**Summary:**
All parameter dictionaries in ATTRIBUTE_DISCARDING now have a `control_name` field for UI/control mapping, following the param_prefix convention.
