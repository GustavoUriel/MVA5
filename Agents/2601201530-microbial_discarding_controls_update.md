# 2601201530-microbial_discarding_controls_update.md

## Change Summary
- Updated the generation of input controls for microbial discarding policies in the analysis editor UI.
- All input controls now use the `control_name` field from each parameter definition in `metadata/MICROBIAL_DISCARDING.py` for their `id` and `name` attributes.
- The checkboxes for enabling/disabling each discarding policy now use the policy's `control_name` for their `id` and `name` attributes.
- This ensures all controls are uniquely and consistently named for backend and frontend integration.

## Files Modified
- `app/static/js/dataset_analysis.js`

## Implementation Details
- The `displayMicrobialDiscardingPolicies` function now uses `policy.control_name` for checkbox controls.
- The `generateParameterInputs` function now uses `paramConfig.control_name` for all input/select controls, falling back to the previous naming if not present.

## Impact
- UI controls for microbial discarding policies are now fully aligned with metadata definitions.
- This improves reliability for form data collection and backend processing.

---
Change completed: All microbial discarding controls now use their metadata-defined names and IDs.