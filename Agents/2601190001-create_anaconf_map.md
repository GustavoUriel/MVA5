# 2601190001 - create_anaconf_map

## Action
- Created `metadata/temp/map.py` — a small script which parses `metadata/temp/anaconf.html` and builds a hierarchical map of element names (tabs indicate nesting). When run it writes `anaconf_map.txt` next to the HTML.

## Files added
- `metadata/temp/map.py`

## Reason
- User requested a hierarchical map of elements in `anaconf.html` saved as `metadata/temp/map.py`.

## Summary of changes
- Added `map.py` which parses the HTML using Python's stdlib `html.parser` and exposes `MAP` string variable. Running the script will also write `anaconf_map.txt` with the generated map.

## Follow-up
- Ran `map.py` and saved the generated hierarchical map as `metadata/temp/anaconf_map.txt` and also as `metadata/temp/map.txt` per user request.

## Final summary
- Created `metadata/temp/map.py` and `metadata/temp/map.txt` containing the hierarchical element map extracted from `anaconf.html`.

## Additional files
- Created `metadata/temp/map_gen.py` — a generator script that parses `anaconf.html` directly and writes a readable `map.txt`.

## Final note
- `metadata/temp/map.txt` now contains a human-readable hierarchical map (labels, control types, names, and values) generated from `anaconf.html`.
