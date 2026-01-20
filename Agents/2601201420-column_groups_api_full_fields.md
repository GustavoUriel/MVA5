# 2601201420-column_groups_api_full_fields.md

## Date: 2026-01-20 14:20

### Change
- Updated the `/dataset/<int:dataset_id>/metadata/column-groups` API endpoint in `app/modules/datasets/datasets_bp.py` to return all fields from each group in `metadata/COLUMN_GROUPS.py`.
- Now, every group object in the API response includes all keys/values from the source dict (e.g., `title`, `name`, `control_name`, `columns`, etc.), plus a `group_key` for reference.

### Summary
The column groups API now exposes the complete metadata for each group, enabling the frontend to access all information defined in `COLUMN_GROUPS.py`.
