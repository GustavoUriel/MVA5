2601231200 - Create fileCuration module

What I changed
- Added a new module: `app/scripts/Curation/fileCuration.py`.
  - Functions added:
    - `columnNameNormalization(df)` — normalize column names to lowercase_snake_case.
    - `identify_file_type(df_or_path)` — detect 'patients' / 'taxonomy' / 'brackens' using metadata.COLUMNS.IDENTIFICATOS and MEDICINES.
    - `InvalidRowsRemover(df, file_type)` — drop rows missing identifier data.
    - `fixMedicines(df)` — medicines-fixing logic adapted from the project's original `fixMedicines.py` (works with normalized column names).
    - `_save_back(df, path)` — rotate original and save processed CSV (returns success flag).
    - `curate(input_data)` — top-level pipeline accepting either a DataFrame (returns DataFrame) or a path (backs up original and overwrites; returns bool).

Notes / Rationale
- The module is intentionally minimal and focuses on processing/curation logic
  (no routes or HTML). It relies on `metadata/COLUMNS.py` for identification and
  uses the project's existing rotate/save helpers via `curation.py`.

Summary
- Created `app/scripts/Curation/fileCuration.py` implementing the requested
  six functions and pipeline. No existing files were modified. The new
  module is ready to be imported and used from other scripts or tests.
