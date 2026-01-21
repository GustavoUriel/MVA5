# 2601161215-fix_microbial_discarding_show_hide.md

## Summary
Updated the Microbial Discarding Policy section in the analysis editor to be compatible with the new API response structure. The API now returns `microbial_discarding_policies` as an array of policies with updated field names and structure.

## Changes Made

### JavaScript Updates (dataset_analysis.js)
1. **loadMicrobialDiscardingPolicies()**: Modified to access `data.microbial_discarding_policies` instead of `data.discarding_policies`, and removed the object-to-array conversion since it's now an array.

2. **displayMicrobialDiscardingPolicies()**: Updated to use new field names:
   - `policy.key` → `policy.policy_key`
   - `policy.name` → `policy.label`
   - Checkbox ID: `id="${policy.control_name}"` → `id="microbial_policy_${policy.policy_key}"`
   - Card IDs and data attributes updated to use `policy.policy_key`

3. **getMicrobialDiscardingPolicyInfo()**: Changed the find condition from `p.key === policyKey` to `p.policy_key === policyKey`

4. **Event listeners and toggle functions**: Updated to use `policy.policy_key` for IDs and keys.

### Parameter Handling
- The `generateParameterInputs()` function already correctly uses `paramConfig.control_name` for input IDs and names, which matches the new API structure.
- Parameters are now collected using their `control_name` as the key in the parameters object.

### Collection Logic
- `collectMicrobialDiscardingPolicies()` correctly collects parameters by `input.name`, which is now the `control_name` from the API.

## API Compatibility
The code now expects the API response in this format:
```json
{
  "microbial_discarding_policies": [
    {
      "policy_key": "prevalence_filtering",
      "label": "Prevalence Filtering",
      "description": "...",
      "enabled": false,
      "parameters": {
        "param_key": {
          "control_name": "MiDi_Prevalence_detection_threshold",
          "type": "float",
          "label": "Detection Threshold",
          ...
        }
      },
      "info": {...}
    }
  ],
  "success": true
}
```

## Validation
- All IDs and names now use the specified `control_name` values from the API.
- The UI correctly displays policy labels and descriptions.
- Parameter inputs have proper IDs and names for form collection.
- Event handling and toggling work with the new structure.