# 2601221210-fix_patient_count_route

Date: 2026-01-22 12:10

Issue:
- `/dataset/<dataset_id>/file/<file_id>/patient-count` returned 404 when frontend passed numeric file IDs.
- Root cause: Route and handler expected a `relative_path` and searched by `file_path.endswith(basename)`, but frontend uses numeric file IDs.

Files changed:
- app/modules/datasets/datasets_bp.py
  - Updated route decorator to use `<int:file_id>` and changed function signature to `get_patient_count(dataset_id, file_id)`.
  - Replaced path-based query with `DatasetFile.query.filter_by(id=file_id, dataset_id=dataset_id).first_or_404()`.
  - Updated debug log to include `file_id`.

Reasoning:
- Align backend route with frontend usage (file ID), making lookup direct and reliable.

Summary:
- Patient-count endpoint now accepts a numeric `file_id` and queries by ID; should resolve 404s when frontend provides file IDs.
