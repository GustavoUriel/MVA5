Date: 2601191015
Action: Add dataset-scoped GET endpoint to return saved analysis JSON

Files changed:
- app/modules/datasets/datasets_bp.py

Summary of change:
- Added route `GET /dataset/<dataset_id>/analysis/<filename>` implemented as `load_analysis_file`.
- The route validates the filename (blocks traversal), constructs the per-dataset analysis folder under `instance/users/<user_email>/<dataset_id>/analysis`, and returns the JSON content if the file exists.
- Handles JSON decode errors and other exceptions with appropriate HTTP error responses.

Why:
- The frontend attempted to fetch saved analysis JSON files (e.g., `unono_c.json`) and received 404. A dedicated route was needed to serve saved analysis files from the per-dataset folder.

Final summary:
- Added a secure GET endpoint to serve saved analysis files for a dataset. This should resolve frontend 404s when loading an analysis by filename.
