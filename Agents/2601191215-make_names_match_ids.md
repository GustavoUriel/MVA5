# 2601191215 - Make dynamic control names match their ids

Date: 2026-01-19 12:15

Summary
-------
Updated `app/static/js/dataset_analysis.js` so dynamically generated user inputs and card containers use `name` attributes that match their `id` attributes where safe to do so. Radio groups that require a shared `name` for grouping behavior were left intact; their card containers now include `name` attributes matching their ids.

Files changed
-------------
- `app/static/js/dataset_analysis.js`:
  - Column group checkboxes: `id="group_${groupKey}"` now `name="group_${groupKey}"`.
  - Discarding policy checkbox: `id="policy_${policy.key}"` now `name="policy_${policy.key}"`.
  - Discarding policy body: `id="policy_body_${policy.key}"` now has `name="policy_body_${policy.key}"`.
  - Policy parameter inputs: `id` and `name` already set to `${policyKey}_param_${paramKey}` (no change).
  - Sample timepoint checkboxes: `id="sample_tp_${tp.key}"` now `name="sample_tp_${tp.key}"`.
  - Stratification checkboxes: `id` and `name` are `strat_${key}` (already matched).
  - Analysis comparison checkboxes: `id="analysis_method_${m.key}"` now `name="analysis_method_${m.key}"`.
  - Microbial discarding policy checkbox and body: `id` and `name` set to match (`microbial_policy_${policy.key}` and `microbial_policy_body_${policy.key}`).
  - Microbial grouping card body: `id` and `name` set to `microbial_grouping_body_${method.key}`. Radio `name` preserved as `microbialGroupingMethod` to keep grouping behavior.

Verification notes
------------------
- Collector functions in `dataset_analysis.js`:
  - `collectDiscardingPolicies`, `collectMicrobialDiscardingPolicies`, and `collectMicrobialGrouping` read parameter values from `input.name` and store them keyed by `input.name`.
  - Since parameter inputs have `name` equal to their ids (`${policyKey}_param_${paramKey}`), collectors will produce parameter maps using those ids as keys. This ensures uniqueness across different policy/method cards.
  - Radio inputs for microbial grouping still share `name="microbialGroupingMethod"` to preserve mutual exclusion; their containing card bodies now have `name` attributes matching their ids.

Next steps
----------
- If you prefer saved configuration parameters to be stored without the `${policyKey}_` prefix, I can update the collectors to strip that prefix when grouping parameters under the policy key.
- Run the app and exercise the Analysis -> Create new analysis UI to confirm behavior in the browser.

End of log.
