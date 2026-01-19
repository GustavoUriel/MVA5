# Sample Timepoints Comparison

Purpose
- UI and client-side logic to let users compare a primary Bracken timepoint with one or more other timepoints.

UI
- Added a Sample Timepoints Comparison card to the analysis editor (`app/templates/dataset/analysis_config.html`).
- Shows the currently selected primary timepoint (from Bracken Time Point Selection) and a list of other timepoints as checkboxes.
- The checkbox corresponding to the currently selected primary timepoint is disabled and unchecked.
- Buttons: `Select All` and `Clear All` for convenience.
- Summary area shows the number selected.

Note: updated to align with `320.TimePointsComparison.md` and `110.DataSourcesSelect.md` for consistent naming of timepoint analyses and delta definitions. Use the `TIMEPOINT_ANALYSES` mapping from the step document as the authoritative config when implementing comparisons.

Client behavior (JS)
- `app/static/js/dataset_analysis.js` now:
  - Calls `DatasetUtils.api.getBrackenTimePoints(datasetId)` to populate available timepoints.
  - `displaySampleTimepoints(timePoints)` renders checkboxes for all timepoints.
  - `updateSampleTimepointsVisibility()` hides/disables the checkbox that matches the selected primary timepoint and updates the summary.
  - `collectSampleTimepoints()` returns selected comparison timepoints and is included in the analysis configuration saved by the editor.
  - Global helpers `selectAllSampleTimepoints()` / `clearAllSampleTimepoints()` added.

Server endpoints used
- `GET /dataset/<dataset_id>/metadata/bracken-time-points` — returns available Bracken timepoints (used to populate both the primary combobox and the comparison list).
- `POST /dataset/<dataset_id>/analysis/save` — analysis configuration save endpoint (now receives `sample_timepoints` as part of `configuration`).
- `GET /dataset/<dataset_id>/file/<file_id>/patient-count` — used by extreme timepoint calculations (unchanged but relevant).

Notes
- The change is UI-first and avoids server schema modifications. The `sample_timepoints` array is added to the saved configuration JSON so back-end consumers can act on it.
- Metadata helper `get_time_points()` was added to `metadata/BRACKEN_TIME_POINTS.py` to help construct a list of timepoints if needed by API handlers.

