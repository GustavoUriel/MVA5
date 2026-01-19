# 2601191210 - Save analysis editor full DOM

## Intent
Add client-side serialization of the Analysis Editor DOM and persist it inside the analysis JSON saved under `instance/users/<user_email>/analysis/` so the full editor state (controls, values, checked states, and structure) is stored alongside the structured `configuration`.

## Changes made

- app/static/js/dataset_analysis.js
  - Added `collectFullAnalysisEditor()` to `DatasetAnalysisManager` which recursively serializes the `#analysisEditorSection` DOM subtree into a hierarchical JSON object capturing element tag, id, name, classes, attributes (skipping very large `data-*` values), form control `value` and `checked` states, text nodes, and children.
  - Updated `saveAnalysis()` to call `collectFullAnalysisEditor()` and include the resulting `full_dom` in the POST payload to `/dataset/<id>/analysis/save`.

- app/modules/datasets/datasets_bp.py
  - Updated `save_analysis_configuration` to accept an optional `full_dom` key from the incoming JSON and persist it into the saved analysis JSON file under the `full_dom` key.
  - Added a `modified_at` timestamp at save time.

## Rationale
Storing the full DOM snapshot preserves the exact editor state for later restore or debugging. The change is minimal and follows existing save patterns.

## Notes
- The serializer skips data-* attributes longer than 1000 characters to avoid embedding huge blobs; adjust if necessary.
- Consider size/cost: full DOM snapshots can be large. If needed, compress or limit size on client or server.

## Summary
- Implemented client-side DOM serialization and persisted it in the analysis JSON file under `instance/users/<user_email>/analysis/` as `full_dom`.

