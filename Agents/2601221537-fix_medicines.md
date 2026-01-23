2601221537 - fix_medicines
==========================

Date: 2026-01-22 15:37

Change
------
- Added `app/scripts/data_curation/fixMedicines.py`.

What it does
------------
- Locates the latest `instance/patients*.csv` file.
- For each drug defined in `metadata.COLUMNS.MEDICINES`:
  - Parses `<drug>_start_date`/`<drug>_end_date` and their `_Eng` counterparts.
  - If the treatment started within 10 days before `First_Transplant_Date`
    and stopped within 10 days after the transplant, the drug indicator
    for that row is set to `0` (for both main and `_Eng` columns separately).
  - Merges the main and `_Eng` indicator columns into a single
    `<drug>` column (keeps `1` if either was `1`).
  - Deletes the start/end date columns and the `_Eng` indicator column.

Output
------
- Writes a fixed CSV next to the original file with suffix `_medicines_fixed.csv`.

Notes
-----
- Dates are parsed using `m/d/YYYY`. Missing or invalid dates are not
  treated as satisfying the peri-transplant window and therefore those
  indicators remain unchanged.

Summary
-------
Created `fixMedicines.py` to apply the peri-transplant filtering and
merge `_Eng` columns; wrote this log entry.
