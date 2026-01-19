# 2601181535-fix_stratification_display_datasetjs.md

## Change Summary
- **File:** app/static/js/dataset.js
- **Change:** Updated `displayStratifications` to accept the new flat dictionary format from the backend, rendering each stratification as a card. This fixes the TypeError and ensures stratifications display correctly in the UI.

## Reason
- The backend now returns a flat dictionary of stratifications, but the old code expected an array of group objects. This update aligns the frontend with the backend response.

## Least Invasive Protocol
- Only the display function was changed. No logic or metadata was altered elsewhere.

## Summary
- Population Sectors Comparison stratification options will now display correctly in the legacy UI.
