# 2601190945 - Fix analysis storage path to include dataset id

## Intent
Analysis JSON files were being saved under `instance/users/<user>/analysis/...` but should be saved under `instance/users/<user>/<dataset_id>/analysis/...` so analyses are grouped per-dataset.

## Changes made
- Modified `app/modules/datasets/datasets_bp.py`:
  - `save_analysis_configuration`: create per-dataset folder `instance/users/<user_email>/<dataset_id>/analysis` and update `relative_path` stored in the JSON to include the `dataset_id` segment.
  - `list_saved_analyses`: look into per-dataset analysis folder when enumerating saved analyses.
  - `delete_analysis`, `duplicate_analysis`, `rename_analysis`: updated to operate on per-dataset analysis folder; updated duplicate's `relative_path` to include dataset id.

## Rationale
Existing behavior saved analysis files in a flat user-level folder which caused files for different datasets to be mixed and prevented proper scoping. Grouping analysis files by dataset keeps data organized and matches expected storage layout.

## Summary
- Files are now saved under `instance/users/<user_email>/<dataset_id>/analysis/`.
- Duplicate operation updates `relative_path` to reference the new per-dataset path.

If there are other places that assume the old path, they should be reviewed (e.g., any scripts or tooling referencing user analysis paths).
