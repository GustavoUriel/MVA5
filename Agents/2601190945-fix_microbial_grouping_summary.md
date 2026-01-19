# 2601190945 - Fix microbial grouping summary null reference

Date: 2026-01-19 09:45

Issue:
- JS runtime TypeError: Cannot read properties of null (reading 'textContent') in `updateMicrobialGroupingSummary` when selecting a microbial grouping option.

Cause:
- The function assumed the label next to the radio input always contains a `<strong>` element. Recent template/markup changes render the method name as plain text within the label (with a `<small>` for description), so `label.querySelector('strong')` returned null and caused an exception.

Changes made:
- Modified `app/static/js/dataset_analysis.js` (`updateMicrobialGroupingSummary`) to safely obtain the method name:
  - Check for a `<strong>` element first.
  - If absent, fall back to the first text node within the label.
  - As a last resort, use the full `label.textContent` trimmed.

Files changed:
- app/static/js/dataset_analysis.js

Summary:
- Prevents the TypeError and ensures the microbial grouping summary text updates correctly when a method is selected.

