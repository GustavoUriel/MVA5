# 2601182030-stratification_cards_fullwidth.md

## Change
- Updated `app/static/js/dataset_analysis.js` to render Population Stratification cards as full-width elements and to display only the stratification name and the `subgroups` list.

## Files modified
- `app/static/js/dataset_analysis.js`

## Rationale
The stratification cards previously used a multi-column layout and displayed descriptive text and parameter blocks between the stratification name and the subgroups list. The UI requested a simpler layout: keep the stratification name and the subgroups list only, and make the cards use the full width for better readability.

## Implementation notes
- Replaced the column classes `col-md-6 col-lg-4` with `col-12` so each card spans the container width.
- Removed inline rendering of `stratification.description`, `groupInfoHtml`, and `paramsHtml` from the card body so that only the name and `${subgroupsHtml}` are shown.

## Testing performed
- Confirmed the JS file was updated. Recommend loading the app and navigating to Analysis → Pre-Analysis → Population Sectors Comparison (or wherever stratifications appear) and expanding the stratification list to verify each card is full-width and shows only the name + subgroups.

## Summary
Simplified stratification card presentation and widened cards to full container width for improved clarity.
