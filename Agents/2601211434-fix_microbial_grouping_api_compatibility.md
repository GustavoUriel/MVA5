# 2601211434-fix_microbial_grouping_api_compatibility.md

## Summary
Updated the Microbial Grouping section in `dataset_analysis.js` to be compatible with the new API response structure. The API now returns an array called `microbial_grouping_methods` with each method having `method_key`, `label`, `control_name`, and `parameters`. Updated field references, used `control_name` for radio button IDs, maintained radio button exclusivity with shared name "microbialGroupingMethod", and ensured default values are pre-filled using the `default` field.

## Changes Made
- **loadMicrobialGroupingPolicies**: Changed to access `data.microbial_grouping_methods` instead of `data.grouping_methods`.
- **displayMicrobialGroupingPolicies**: 
  - Updated to use `method.method_key` for keys, `method.name` for display names.
  - Used `method.control_name` for radio button IDs.
  - Used `method.enabled` for checked state and body visibility.
  - Updated generateParameterInputs call to use `method.method_key`.
  - Updated event listener to use `method.control_name` for getElementById.
- **getMicrobialGroupingInfo**: Changed find condition from `m.key` to `m.method_key`.

## Validation
- Code structure verified manually.
- No syntax errors introduced.
- Maintains existing functionality for radio button single selection and parameter handling.

## Correction
- Changed `method.label` to `method.name` for display text.
- Changed `method.default` to `method.enabled` for checked state and visibility.