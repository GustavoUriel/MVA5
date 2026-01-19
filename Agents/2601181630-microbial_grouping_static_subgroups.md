# 2601181630-microbial_grouping_static_subgroups.md

## Date: 2026-01-18 16:30

## Change Summary
- Updated microbial grouping configuration so that users can only select the grouping strategy, not individual subgroups.
- All subgroup selection parameters were removed from each grouping in `metadata/MICROBIAL_GROUPING.py`.
- Each grouping now contains a static description of its subgroups, shown in the UI.
- Added a "No Grouping" option to the grouping strategies.
- Updated the frontend (`app/static/js/dataset_analysis.js`) so that only static subgroup descriptions are shown in each card, with no input fields.

## Details
- **metadata/MICROBIAL_GROUPING.py**: All `parameters` now only contain a single static description for subgroups. Added a `not_grouping` option.
- **app/static/js/dataset_analysis.js**: The `generateParameterInputs` function now only renders static text for microbial grouping cards. The UI no longer renders any input fields for subgroups.

## Impact
- Users can now only select which grouping strategy to use. All subgroups for a strategy are always included as described.
- The UI is simplified and matches the new requirements.

## Final Summary
- Microbial grouping cards now only show static subgroup descriptions. No subgroup selection is possible. A "No Grouping" option is available. All changes are least invasive and logged here.
