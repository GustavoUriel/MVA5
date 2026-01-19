# 2601181314-fix_attributes_groups_selection

Date: 2026-01-18 13:14

Change: Fix Attributes Groups Selection rendering and summary calculation in the analysis editor.

Files modified:

- app/static/js/dataset_analysis.js

What I changed:

- Updated `displayColumnGroups` to handle backend responses that return an ordered list of column groups (array of objects with `name` and `columns`) as well as legacy dictionary/object shapes. The function now:
  - Normalizes the data into an array.
  - Uses the `columns` (or `fields`) key to compute field counts.
  - Renders checkboxes with a `data-field-count` attribute and an inline `onchange` that updates the summary.
  - Ensures the `#columnGroupsContent` container is displayed after groups load.

- Updated `updateColumnGroupsSummary` to:
  - Read selected group names for the selection summary.
  - Sum `data-field-count` across selected groups to display the total attributes count (fallback to number of selected groups if counts not available).

APIs used by this feature (frontend):

- `GET /dataset/<dataset_id>/metadata/column-groups` — returns column groups metadata (backend returns `column_groups` as an ordered list of objects with `name` and `columns`).
- `GET /dataset/<dataset_id>/files/api` — used to populate file dropdowns for data sources.
- `GET /dataset/<dataset_id>/metadata/attribute-discarding` — attribute discarding policies (used elsewhere in the editor).
- `GET /dataset/<dataset_id>/metadata/bracken-time-points` — bracken time points.
- `GET /dataset/<dataset_id>/metadata/stratifications` — stratifications.

Notes / Rationale:

- The backend returns `column_groups` as a list of `{name, columns}` items. The previous frontend expected an object mapping keys to `{fields}` and therefore displayed numeric indices as group names and "0 fields". Normalizing both shapes prevents regressions and supports either response format.
- Adding `data-field-count` enables accurate total attribute count in the summary.

Summary:

Patched `displayColumnGroups` and `updateColumnGroupsSummary` in `app/static/js/dataset_analysis.js` to correctly render attribute groups, show their field counts, and compute a correct total attributes summary. The column groups section is now revealed after successful load.
