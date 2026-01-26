"""
Fix medicines columns in patients CSV files.

Behavior:
- Find the latest patients CSV in `instance/patients*.csv`.
- For each drug name listed in `metadata.COLUMNS.MEDICINES`:
    - Look for columns: `<drug>`, `<drug>_start_date`, `<drug>_end_date`,
        `<drug>_Eng`, `<drug>_start_dateEng`, `<drug>_end_dateEng`.
    - If the patient has a `1` in the drug column and the start/end dates
        indicate the treatment started within 10 days before transplant and
        stopped within 10 days after transplant, set that drug indicator to `0`.
    - Repeat the same for the `_Eng` columns.
    - Merge the two indicators into a single column named `<drug>` with `1`
        if either of the two original columns is `1`.
    - Drop the four date columns for that drug.

Notes:
- Dates are parsed as `m/d/YYYY` and missing/invalid dates are ignored
    (in which case the indicator is left unchanged).

The script writes a new CSV next to the original file with suffix
    `_medicines_fixed.csv`.
"""

from __future__ import annotations

import glob
import os
from pathlib import Path
from typing import Iterable

import pandas as pd

from metadata.COLUMNS import MEDICINES



def iterate_drug_names(medicines_dict) -> Iterable[str]:
    """Yield each drug name from the MEDICINES dictionary's lists."""
    for group in medicines_dict.values():
        for drug in group:
            yield drug


def parse_date_series(df: pd.DataFrame, col: str) -> pd.Series:
    """Parse a date column in m/d/YYYY format; return datetime64[ns] or NaT."""
    if col not in df.columns:
        return pd.Series(pd.NaT, index=df.index)
    # Handle duplicate column names by selecting the first occurrence
    try:
        return pd.to_datetime(df[col], format="%m/%d/%Y", errors="coerce")
    except (ValueError, KeyError):
        # If there are duplicate columns, use iloc to select the first occurrence
        col_indices = [i for i, c in enumerate(df.columns) if c == col]
        if col_indices:
            return pd.to_datetime(df.iloc[:, col_indices[0]], format="%m/%d/%Y", errors="coerce")
        return pd.Series(pd.NaT, index=df.index)


def fix_medicines_file(path: str | Path) -> Path:
    """Process the given patients CSV and write a fixed copy.

    Returns the path to the written file.
    """
    df = pd.read_csv(path, dtype=str)
    df_fixed = fix_medicines_df(df)

    # Write output next to input with suffix
    src = Path(path)
    out = src.with_name(src.stem + "_medicines_fixed" + src.suffix)
    df_fixed.to_csv(out, index=False)
    return out


def fix_medicines_df(df: pd.DataFrame) -> pd.DataFrame:
    """Process the medicines logic on a DataFrame and return the fixed DataFrame.

    This function mirrors the logic previously in `fix_medicines_file` but
    operates on an in-memory DataFrame so it can be called from
    `curation.process_file`.
    """
    df = df.copy()

    # Parse transplant date column (case-insensitive)
    transplant_col = None
    for col in df.columns:
        if col.lower() == "first_transplant_date":
            transplant_col = col
            break
    if transplant_col is None:
        raise KeyError("Column 'First_Transplant_Date' not found in DataFrame")
    transplant = pd.to_datetime(df[transplant_col], format="%m/%d/%Y", errors="coerce")
    transplant = pd.Series(transplant, index=df.index)

    cols = list(df.columns)
    
    def find_column_case_insensitive(target_name: str) -> str | None:
        """Find a column by case-insensitive name matching.
        
        Returns the actual column name if found, None otherwise.
        """
        target_lower = target_name.lower()
        for col in cols:
            if col.lower() == target_lower:
                return col
        return None

    def find_adjacent_dates(col_name: str, start_keywords=("start", "Start", "Start_Date", "Start_date")):
        """Find next two columns after `col_name` and return them as (start_col, end_col) if they look like dates.

        This handles spreadsheets where columns are laid out as:
        Drug, Start_Date, End_Date, Drug_Eng, Start_DateEng, End_DateEng, ...
        If the exact paired columns aren't present by name, we use position-based
        inference: next two columns after the drug column are treated as start/end.
        """
        # First try case-insensitive match
        actual_col = find_column_case_insensitive(col_name)
        if actual_col is None:
            return (None, None)
        idx = cols.index(actual_col)
        # candidate by position
        start_col = cols[idx + 1] if idx + 1 < len(cols) else None
        end_col = cols[idx + 2] if idx + 2 < len(cols) else None
        return (start_col, end_col)

    for drug in iterate_drug_names(MEDICINES):
        # Find actual column names (case-insensitive)
        main_col_target = drug
        eng_col_target = f"{drug}_Eng"
        main_col = find_column_case_insensitive(main_col_target)
        eng_col = find_column_case_insensitive(eng_col_target)

        # If columns don't exist, use lowercase names (will be created)
        if main_col is None:
            main_col = main_col_target
        if eng_col is None:
            eng_col = eng_col_target

        start_col, end_col = find_adjacent_dates(main_col)
        start_eng, end_eng = find_adjacent_dates(eng_col)

        # Parse date columns (will yield NaT for missing/invalid)
        start = parse_date_series(df, start_col) if start_col else pd.Series(pd.NaT, index=df.index)
        end = parse_date_series(df, end_col) if end_col else pd.Series(pd.NaT, index=df.index)
        start_e = parse_date_series(df, start_eng) if start_eng else pd.Series(pd.NaT, index=df.index)
        end_e = parse_date_series(df, end_eng) if end_eng else pd.Series(pd.NaT, index=df.index)

        # Ensure indicator columns exist; create with 0 if they don't
        if main_col not in df.columns:
            df[main_col] = 0
        if eng_col not in df.columns:
            df[eng_col] = 0

        # Normalize indicator columns to integers 0/1
        df[main_col] = pd.to_numeric(df[main_col], errors="coerce").fillna(0).astype(int)
        df[eng_col] = pd.to_numeric(df[eng_col], errors="coerce").fillna(0).astype(int)

        # Define the peri-transplant windows
        started_within_window = (start >= (transplant - pd.Timedelta(days=10))) & (start <= transplant)
        stopped_within_window = (end >= transplant) & (end <= (transplant + pd.Timedelta(days=10)))

        # For main column: where indicator==1 and both start/end satisfy window -> set to 0
        mask_main_to_zero = (df[main_col] == 1) & started_within_window & stopped_within_window
        df.loc[mask_main_to_zero, main_col] = 0

        # Same for _Eng columns
        started_within_window_e = (start_e >= (transplant - pd.Timedelta(days=10))) & (start_e <= transplant)
        stopped_within_window_e = (end_e >= transplant) & (end_e <= (transplant + pd.Timedelta(days=10)))
        mask_eng_to_zero = (df[eng_col] == 1) & started_within_window_e & stopped_within_window_e
        df.loc[mask_eng_to_zero, eng_col] = 0

        # Merge the two indicator columns into the main column (keep 1 if any is 1)
        merged = ((df[main_col].fillna(0).astype(int)) | (df[eng_col].fillna(0).astype(int))).astype(int)
        
        # Use lowercase drug name as the final column name
        final_col_name = drug.lower()
        df[final_col_name] = merged
        
        # If main_col was different (capitalized), drop it and keep the lowercase version
        if main_col != final_col_name and main_col in df.columns:
            df.drop(columns=[main_col], inplace=True)

        # Drop date columns if present (drop only those we detected)
        for c in (start_col, end_col, start_eng, end_eng):
            if c and c in df.columns:
                df.drop(columns=[c], inplace=True)

        # Also drop the _Eng indicator column (we kept merged into main)
        if eng_col in df.columns and eng_col != final_col_name:
            df.drop(columns=[eng_col], inplace=True)
        
        # Update cols list after dropping columns
        cols = list(df.columns)

    return df



