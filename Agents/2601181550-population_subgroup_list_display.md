# 2601181550-population_subgroup_list_display.md

## Change Summary
- **File:** metadata/POPULATION_SUBGROUPS.py
  - Added a `subgroups` field to each population grouping, listing the subgroups and their assignment conditions.
- **File:** app/modules/datasets/datasets_bp.py
  - Updated the stratification API to include the `subgroups` field in the response.
- **File:** app/static/js/dataset.js
  - Updated the UI to render the subgroups list (with name and condition) in each stratification card, below the description and group_info.

## Reason
- Users requested that each card include the description and a list of the subgroups in each grouping, with the conditions for each subgroup, for technical clarity and transparency.

## Least Invasive Protocol
- Only the relevant fields and display logic were updated. No unrelated logic was changed.

## Summary
- Each stratification card now shows the description, a technical list of subgroup definitions, and a clear list of subgroups with assignment conditions, all sourced from the metadata file.
