## Archive unused handlers — 2026-01-23 12:45

Summary:

- Created/updated delegating wrappers and archived implementations for handlers marked as unused in `endpoints.md`.
- Files changed:
  - `app/modules/editor/editor_bp.py` — replaced `editor_save` implementation with a delegator to `archive.archived_handlers.editor_save`.
  - `app/modules/datasets/datasets_bp.py` — replaced implementations of the following handlers with delegators to `archive.archived_handlers`: `new_dataset`, `delete_dataset_file` (datasets variant), `delete_dataset`, `calculate_remaining_attributes`, `calculate_remaining_microbes`, `get_clustering_method`, `get_cluster_representative_method`, `sanitize_dataset_data`, `get_analysis_method`, `get_metadata`.
  - `endpoints.md` — updated entries that were previously marked UNUSED to now indicate ARCHIVED (moved to `archive/archived_handlers.py`).

Rationale:

- Followed the project's least-invasive modification protocol: implementations preserved in `archive/archived_handlers.py`, original route functions converted to thin delegators that import and call the archived code. This keeps routes functional (no import-time failures) while moving the implementation bodies out of the primary blueprint files.

Notes / next steps:

- Run a quick smoke import check and start the dev server to ensure no runtime import issues. I updated only function bodies and added imports inside the delegators to avoid introducing circular imports at module load time.
- If you'd like, I can open a branch `archive-unused-handlers`, commit these changes, and create a PR. Tell me if you want that.

Summary of changes performed at bottom of file:

- Replaced `editor_save` with delegator.
- Replaced multiple `datasets_bp` handlers with delegators.
- Annotated `endpoints.md` entries as ARCHIVED.
