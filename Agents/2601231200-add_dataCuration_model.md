# 2601231200 - Add dataCuration model

Date: 2026-01-23 12:00 UTC (timestamped filename: 2601231200)

Files added:
- app/model/dataCuration.py

Purpose:
- Introduce a reusable `run_pipeline` function that accepts either a
  pandas DataFrame or a filepath. The pipeline:
  1. Reads the CSV if a filepath was provided.
  2. Detects file type using `app.scripts.files.findFileType()`.
  3. Normalizes column names to lowercase_snake_case.
  4. Removes invalid rows based on `IDENTIFICATORS`.
  5. Applies medicines-fixing using the existing
     `app.scripts.Curation.fixMedicines.fix_medicines_df` for
     patient files.
  6. If input was a filepath the original file is moved to a
     "_orig" backup and the processed CSV is written to the original
     filename.

Notes and decisions:
- If `findFileType` returns `Error` or `unknown` the pipeline returns
  immediately with that status.
- Steps return short status tokens; `run_pipeline` aggregates them into
  a semicolon-separated summary string.
- The medicines step will be skipped for non-`patients` types and will
  return an explanatory status if it cannot run due to missing columns.

Summary of changes:
- Created `app/model/dataCuration.py` implementing the pipeline.
