# 2601200001-add_param_control_name.md

## Change Summary
Added a `control_name` key to every parameter in every method in the `ANALYSIS_METHODS` variable. The value is constructed as the method's `param_prefix` plus the parameter name, as requested.

## Details
- For each method in `ANALYSIS_METHODS`, iterated over its `parameters` dict.
- Added `'control_name': <param_prefix><parameter_name>` to each parameter dict.
- No other logic or structure was changed.

## Reason
This enables UI or API code to reference parameter controls in a consistent, programmatic way.

---

### Final Summary
All parameters in all methods in `ANALYSIS_METHODS` now have a `control_name` key with the correct value. No other changes were made.