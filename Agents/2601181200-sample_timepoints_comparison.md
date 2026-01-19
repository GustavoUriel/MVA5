# 2601181200-sample_timepoints_comparison

Date: 26/01/18 12:00 (YYMMDDHHmm format)

Intent
- Implement the Sample Timepoints Comparison UI and client-side behavior so the user can select a primary Bracken timepoint and choose one or many other timepoints for comparison.

Files changed
- Modified: app/templates/dataset/analysis_config.html
  - Added the `sampleTimepointsCard` block: shows selected timepoint, checkboxes for other timepoints, `Select All` / `Clear All` buttons, and a summary badge.

- Modified: app/static/js/dataset_analysis.js
  - After loading bracken time points, render sample comparison checkboxes via `displaySampleTimepoints(timePoints)`.
  - Added methods: `displaySampleTimepoints`, `updateSampleTimepointsVisibility`, `updateSampleTimepointsSummary`, `collectSampleTimepoints`.
  - Ensure the selected primary timepoint is disabled in the comparison list.
  - Include `sample_timepoints` in `collectAnalysisConfiguration()` so selected comparisons are saved with analysis configuration.
  - Added global helpers: `selectAllSampleTimepoints()` and `clearAllSampleTimepoints()`.

- Modified: metadata/BRACKEN_TIME_POINTS.py
  - Added `get_time_points()` helper that returns a list of dicts with `key`, `title`, and `description` suitable for API consumption.

- Added: architecture/analysis/Sample_Timepoints_Comparison.md
  - Documentation of UI, JS behavior and server endpoints used.

Summary
- Implemented the UI and client-side logic to show all bracken timepoints for comparison and automatically hide/disable the one selected as primary. The selected comparisons are now included in the saved analysis configuration under `configuration.sample_timepoints`.

