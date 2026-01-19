# 2601190930 - Save full analysis editor DOM

## Intent
Add functionality to save the exact contents and structure of the Analysis Configuration editor into the analysis JSON file stored under `instance/users/<user>/analysis/`.

## Changes made
- app/static/js/dataset_analysis.js
  - Added `collectFullAnalysisEditor()` to `DatasetAnalysisManager` which serializes the `#analysisEditorSection` DOM subtree into a structured JSON object. It captures element tags, ids, classes, attributes (skipping large data-*), text nodes, form control values and checked states, and nested children recursively.
  - Updated `saveAnalysis()` to include the serialized `full_dom` payload alongside the existing `configuration` when calling `/dataset/<id>/analysis/save`.

- app/modules/datasets/datasets_bp.py
  - Updated `save_analysis_configuration` to accept and persist a `full_dom` key in the saved analysis JSON.

## Rationale
The app already had client-side collection for specific configurations; the requirement was to store the exact page contents (visible or hidden) in a file named after the analysis. Adding the DOM snapshot preserves the complete editor state for restore or later editing.

This change is minimal and follows the existing pattern for saving analysis JSON files in `datasets_bp`.

## Notes and next steps
- The DOM snapshot can be large; consider adding size limits or compression if necessary.
- The current serializer skips `data-*` attributes to avoid storing large blobs. If specific data-* attributes are required, adjust the serializer accordingly.
- If you prefer the save endpoints to live in `app/modules/analysis/analysis_bp.py` instead of `datasets_bp.py`, we can refactor them; however, they are dataset-scoped and fit well in `datasets_bp.py`.

## Summary
- Implemented client-side DOM serialization and stored it in the analysis JSON file under `instance/users/<user_email>/analysis/`.

Saved changes summary: added `full_dom` collection in JS and persisted it in the datasets blueprint save endpoint.
