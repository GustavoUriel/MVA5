# 2601181545-population_group_info_technical_list.md

## Change Summary
- **File:** metadata/POPULATION_SUBGROUPS.py
  - Changed each `group_info` from plain text to a technical, structured bullet list describing subgroup definitions and assignment parameters.
- **File:** app/static/js/dataset.js
  - Updated the UI to render `group_info` as a bullet list if it is an array, for technical clarity.

## Reason
- Users requested a more technical, explicit list of subgroups and assignment rules for each population stratification, rather than a plain text description.

## Least Invasive Protocol
- Only the relevant fields and display logic were updated. No unrelated logic was changed.

## Summary
- Each stratification card now shows a technical, structured list of subgroup definitions and assignment parameters, with all static text managed in the metadata file.
