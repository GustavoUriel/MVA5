# 2601231215 - test findFileType with instance CSVs

Date: 2026-01-23 12:15

Change summary:

- Added `tests/test_findFileType.py` to exercise `findFileType` on the
  following files in `instance/`: `taxonomy.csv`, `patients.csv`,
  `bracken.csv`, `patients -erer llc.csv`.

What was changed:

- New file: `tests/test_findFileType.py` which reads each CSV and prints
  the detected type using `app.scripts.files.findFileType`.

Summary of what was done:

- Created a small CLI test harness to run locally and observe outputs.
