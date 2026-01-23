### 2601221250 - Convert `medicines` to dictionary in metadata/COLUMNS.py

Change performed:

- Replaced the `medicines` list-of-lists with a dictionary where keys are the
  medicine group names taken from the existing comments (`Fluoroquinolones`,
  `Penicillins`, `Cephalosporins`, `Macrolides`, `Other_Antibiotics`,
  `Antifungals`). Values are the corresponding lists of normalized column
  identifiers. This makes lookups by group name explicit and easier for
  downstream code.

Files modified:

- `metadata/COLUMNS.py` — `medicines` converted to a dict keyed by group names.

Summary:

Least-invasive change to provide a keyed mapping for medicine groups while
preserving the original notes in comments. No existing identifiers were
renamed; keys are human-readable group names to match the comment labels.

End of log.
