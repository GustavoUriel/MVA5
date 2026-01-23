# 2601231200 - Add Bracken Table Identification Function

## Changes Made
- Added import pandas as pd at the top of metadata/COLUMNS.py
- Added function is_bracken_table(df) to identify bracken tables based on data being numeric from second row.

## Summary
Added functionality to identify bracken tables in the COLUMNS.py file by checking if all values in rows after the first are numeric. This addresses the unknown column names for bracken tables.