# 2601191230 - Add name attributes to Output Options and Column Groups

Date: 26/01/19 12:30

Summary:
- Added missing `name` attributes to several checkbox inputs so each input's `name` matches its `id`.

Files changed:
- `app/static/js/dataset.js` — column group checkboxes now include `name="colGroupX"` when generated.
- `app/templates/dataset/analysis_config.html` — added `name="includePlots"` and `name="includeRawData"` to output option checkboxes.
- `app/templates/dataset_original.html` — added `name` attributes for `includePlots` and `includeRawData` in legacy template occurrences.

Reasoning:
- Inputs were referenced by `id` in scripts but lacked `name` attributes; adding `name` ensures form-like semantics and meets the requirement that name == id for controls.

Notes:
- The dynamic column group inputs created by `displayColumnGroups` in `dataset.js` now set `name` to the same value as the generated `id` (e.g., `colGroup0`).
- No collector logic was altered; code that reads `document.getElementById(...)` or `input.name` will continue to work. If later you prefer to group parameter names differently when saving, we can update collectors to remap names.

Summary of action performed:
- Ensured Output Options checkboxes `includePlots` and `includeRawData` have `name` matching `id`.
- Ensured dynamically generated column group checkboxes now have `name` matching their generated `id` (colGroup0..colGroupN).

Additional edits (2601191255):
- Added missing `name` attributes to all user input elements in `app/templates/dataset/analysis_config.html` so each `name` equals its `id`.

Files changed in this step:
- `app/templates/dataset/analysis_config.html` — added `name` attributes to the following elements: `analysisName`, `analysisDescription`, `editorPatientFileSelect`, `editorTaxonomyFileSelect`, `editorBrackenFileSelect`, `editorBrackenTimePointSelect`, `selectionModeToggle`, `topPercentage`, `bottomPercentage`, `linkPercentages`, `clusteringMethodSelect`, `clusterRepresentativeMethod`, `analysisMethodSelect`, `reportPDF`, `reportHTML`, `reportCSV`, `includeSummary`.

Reasoning:
- The request required every `<input>`, `<select>`, and `<range>` within the analysis editor to have a `name` identical to its `id`. Changes were kept minimal: only `name` attributes were added where missing.

Summary of action performed (this step):
- Added `name` attributes to inputs and selects in `analysis_config.html` so form-like code and any code that relies on `input.name` will have consistent, descriptive keys.
