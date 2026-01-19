# 2601181540-population_group_info_display.md

## Change Summary
- **File:** metadata/POPULATION_SUBGROUPS.py
  - Added a `group_info` field to each subgroup, describing the subgroups and how assignment is calculated.
- **File:** app/modules/datasets/datasets_bp.py
  - Updated the stratification API to include the `group_info` field in the response.
- **File:** app/static/js/dataset.js
  - Updated the stratification card UI to display the `group_info` field in each group card.

## Reason
- Users need to see, for each population stratification, a description of the subgroups and how assignment to each group is calculated. All static text is now sourced from the metadata Python file.

## Least Invasive Protocol
- Only the relevant fields and display logic were updated. No unrelated logic was changed.

## Summary
- Each stratification card now shows a clear explanation of subgroup definitions and assignment logic, with all static text managed in the metadata file.
