# 2601201610-wire_updateAnalysisMethodsVisibility.md

## Change Summary

### 1. Wire up Card Disabling Logic
- **File:** app/static/js/dataset.js
- **Change:** After running `updateAnalysisMethod()` (on dropdown change), now also calls `window.analysisManager.updateAnalysisMethodsVisibility()` if available. This ensures the card disabling logic is triggered when the analysis method is changed.

---

## Final Summary
- The function that visually disables the selected analysis method card is now called after every dropdown change.
- This should fully enable the intended UI behavior for disabling the selected method in the comparison section.
- All changes are logged in this file.
