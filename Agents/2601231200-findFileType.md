# 2601231200 - add findFileType

Date: 2026-01-23 12:00

Change summary:

- Added `findFileType(df)` to `app/scripts/files.py`.

What was changed:

- New file: `app/scripts/files.py` with implementation that:
  - Imports `IDENTIFICATORS` from `metadata/COLUMNS.py` when available.
  - Returns the first IDENTIFICATORS key whose required columns are a
    subset of the DataFrame's columns.
  - If no key matches, samples rows 2..end (up to 20 rows) and returns
    `bracken` if all inspected non-empty values are numeric.
  - Returns `unknown` when no match is found, and `Error` on invalid
    input or unexpected exceptions.

Notes:

- This edit follows the project's least-invasive guideline: a single new
  module was added; existing files were not modified.

Summary of what was done:

- Implemented `findFileType` and created this Agents log file.
