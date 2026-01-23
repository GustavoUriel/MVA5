2601221545 - add_curation
=========================

Date: 2026-01-22 15:45

Change
------
- Added `app/scripts/Curation/curation.py`.

What it does
------------
- Provides helpers to load a CSV into a pandas DataFrame, run a
  sequence of processor callables, rotate the original file to
  `filename_(original).ext`, and save the processed DataFrame to the
  original filename.

Notes
-----
- The module is intentionally small and documented so existing
  processing functions can be passed in as `processors`.

Summary
-------
Created `curation.py` to standardize loading/processing/rotation/saving.
