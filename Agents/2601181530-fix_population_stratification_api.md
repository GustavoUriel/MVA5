# 2601181530-fix_population_stratification_api.md

## Change Summary
- **File:** app/modules/datasets/datasets_bp.py
- **Change:** The /dataset/<id>/metadata/stratifications endpoint now returns a flat dictionary of stratifications keyed by subgroup, each with `name` and `description` fields directly accessible. This matches the frontend's expectations and resolves the issue where stratification names/descriptions appeared as "undefined" in the UI.

## Reason
- The frontend expects a flat object of stratifications, not a nested group/array structure. This change ensures compatibility and correct display.

## Least Invasive Protocol
- Only the API response formatting was changed. No logic or metadata was altered.

## Summary
- Population Sectors Comparison stratification options will now display correct names and descriptions in the UI.
