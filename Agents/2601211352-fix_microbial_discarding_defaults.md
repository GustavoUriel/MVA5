# 2601211352-fix_microbial_discarding_defaults.md

## Summary of Changes
Updated the `generateParameterInputs` function in `dataset_analysis.js` to properly set default values for select controls in the Microbial Discard Policy section.

### Specific Changes
- In the SELECT type handling, changed the comparison from `o.value === paramConfig.default` to `o.label === paramConfig.default` to match the API structure where the default field contains the label text (e.g., "Strict removal") rather than the value (e.g., "strict").

### Reason
The API provides defaults as the human-readable label text, but the code was comparing against the internal value, causing defaults not to be selected in dropdowns.

### Files Modified
- `c:\code\Rena Python\MVA5\app\static\js\dataset_analysis.js`: Updated generateParameterInputs function for select type.

### Testing
- No syntax errors introduced (code structure validated).
- Defaults should now be pre-selected in select controls for microbial discarding policies.

## Summary
Fixed default value selection for select controls in microbial discarding policies by aligning the comparison with the API's default field format (label text).