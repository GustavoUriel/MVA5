# 2601231305 - accept file path or DataFrame in findFileType

Date: 2026-01-23 13:05

Change summary:

- Updated `app/scripts/files.py::findFileType` to accept either a pandas
  DataFrame or a file path (string or PathLike). If a path is provided,
  the function now attempts to load it using `pandas.read_csv` and then
  performs the usual detection.

What was changed:

- Edited `app/scripts/files.py`:
  - Added `os` and `Path` imports.
  - If `df` is a path-like object or string, the file is read into a
    DataFrame before detection. On read failure the function returns
    `Error`.

Summary of what was done:

- Made `findFileType` more flexible by accepting file paths and logging
  the change in this Agents file.
