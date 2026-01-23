from __future__ import annotations

from typing import Optional, Iterable

import pandas as pd


def remove_invalid_values(    df: pd.DataFrame) -> pd.DataFrame:
    """Replace common invalid cell values across the entire DataFrame.

    - invalid_tokens: iterable of string tokens (case-insensitive and stripped)
        that should be considered invalid (e.g. '', 'NA', 'N/A', 'unknown').
    - replace_with: value to use for replacements (defaults to pandas.NA).
    - inplace: if True modify the provided DataFrame, otherwise operate on a copy.

    The function treats any existing NA (pd.isna) as already invalid, and
        additionally replaces string tokens that match the provided list.
    """
    invalid_tokens = {"", "na", "n/a", "none", "null", "nan", "-", "--", "unknown"}
    # Normalize tokens to lower-stripped strings for comparison
    norm_tokens = {str(t).strip().lower() for t in invalid_tokens}

    def _clean_cell(x):
        try:
            if pd.isna(x):
                return pd.NA
        except Exception:
            # If pd.isna raises for some exotic type, fall back to string check
            pass

        if isinstance(x, str):
            s = x.strip()
            if s == "":
                return pd.NA
            if s.lower() in norm_tokens:
                return pd.NA
            return s
        return x

    # Use apply + Series.map to avoid static-analysis issues with applymap
    return df.apply(lambda col: col.map(_clean_cell))


__all__ = ["remove_invalid_values"]
