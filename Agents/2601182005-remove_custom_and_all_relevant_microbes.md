# 2601182005-remove_custom_and_all_relevant_microbes.md

## Change
- Removed `all_relevant_microbes` and `custom_selection` options from `metadata/MICROBIAL_GROUPING.py`.

## Files modified
- `metadata/MICROBIAL_GROUPING.py`

## Rationale
The `all_relevant_microbes` and `custom_selection` grouping options were removed as requested to simplify the available microbial grouping methods and avoid overly broad or user-defined groupings that are handled elsewhere in the UI.

## Notes on `Lactobacillus spp.`
- I searched the file for standalone occurrences of `Lactobacillus spp.` and found only inline occurrences within the `immunomodulatory_bacteria` descriptions (as part of an inline sentence). There is no line that consists only of `Lactobacillus spp.`. The inline references remain intact.

## Testing performed
- Confirmed the two grouping entries were removed from `MICROBIAL_GROUPING.py`.
- Recommend restarting the app and opening Analysis → Pre-Analysis → Microbial Grouping to confirm the removed options no longer appear in the UI.

## Summary
Removed two grouping options and verified no stray standalone `Lactobacillus spp.` line exists in the metadata file.
