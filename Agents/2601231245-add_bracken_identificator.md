# 2601231245 - add 'bracken' IDENTIFICATORS entry

Date: 2026-01-23 12:45

Change summary:

- Added a `'bracken'` entry to the `IDENTIFICATORS` dictionary in
  `metadata/COLUMNS.py`. Since `bracken` files do not have fixed column
  names, the entry is an empty list and a comment explains the detection
  criteria.

What was changed:

- Edited `metadata/COLUMNS.py` to include:

  'bracken': []

  with an adjacent comment describing that `bracken` is detected when
  all values in rows 2..end (skip the first data row) are numeric
  (sampling up to the first 20 rows is recommended).

Summary of what was done:

- Updated `IDENTIFICATORS` to include `bracken` and documented the
  criteria for detection.
