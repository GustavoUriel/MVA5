# 2601191200 - Add unique names to dynamic analysis controls

Date: 2026-01-19 12:00 (YYMMDDHHmm format used in filename)

Summary
-------
Added descriptive and unique `name` attributes to dynamically generated UI controls in `app/static/js/dataset_analysis.js` so that each control's `name` refers to its content and location (policy, method, timepoint, etc.). This improves form parameter collection and prevents collisions between controls generated across different cards/sections.

Files changed
-------------
- `app/static/js/dataset_analysis.js`:
  - Added `name` attributes for:
    - Column group checkboxes: `column_group_${groupKey}`
    - Discarding policy checkboxes: `discarding_policy_${policy.key}`
    - Microbial discarding policy checkboxes: `microbial_discarding_policy_${policy.key}`
    - Policy parameter inputs: `${policyKey}_param_${paramKey}` (number/select/text)
    - Sample timepoint checkboxes: `sample_timepoint_${tp.key}`
    - Analysis comparison checkboxes: `analysis_method_comp_${m.key}`
    - Stratification checkboxes: `strat_${key}`

Rationale
---------
- `collectDiscardingPolicies`, `collectMicrobialDiscardingPolicies`, and other collectors previously relied on `input.name` values that were not unique across policies. By including the policy/method key in the `name`, parameter keys become unique and clearly scoped to their parent card, avoiding collisions when multiple policies/methods expose parameters with identical parameter keys.

Notes
-----
- Radio groups intentionally keep a common group `name` (e.g., microbial grouping radio inputs) to preserve expected grouping behavior.
- The code that collects parameter values (`collectDiscardingPolicies`, `collectMicrobialDiscardingPolicies`, etc.) uses `input.name` to build parameter maps; these collectors will now produce parameter objects keyed by the scoped names (e.g. `policyA_param_threshold`). This is intentional to guarantee uniqueness.

Summary of actions performed
----------------------------
- Updated `dataset_analysis.js` to add `name` attributes to dynamically generated inputs and checkboxes.

If you want the saved configuration keys to strip the policy prefix (so saved parameter objects remain short), I can update the collectors to map names like `policy_param_x` back to `{ param_x: value }` grouped under the policy key when saving instead of storing the full prefixed name.

End of log.
