# 2601201450-add_control_name_to_parameters.md

## Change Summary

On 2026-01-20 at 14:50, the file metadata/ANALYSIS_METHODS.py was updated so that every parameter in every method now includes a `control_name` field. The value of this field is the method's `param_prefix` concatenated with the parameter name, as required.

---

**Summary:**
All parameters in all methods now have a `control_name` key for UI and programmatic reference, following the specified naming convention.
