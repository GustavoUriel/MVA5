from typing import Optional
import os
from pathlib import Path

import pandas as pd

try:
    from metadata.COLUMNS import IDENTIFICATORS
except Exception:
    IDENTIFICATORS = {}


def findFileType(df) -> str:
    """Detect the type of data in a DataFrame or from a file path.

    `df` may be a pandas DataFrame or a file path (str / PathLike). If a
    path is provided, the CSV is loaded with `pandas.read_csv` before
    detection. Returns one of the IDENTIFICATORS keys if all required
    columns for a type are present. If no key matches, checks for
    'bracken' by verifying that rows 2..end (sample up to first 20) contain
    only numeric values (non-numeric non-empty cells make it fail).
    Returns 'unknown' when no type matches, and 'Error' on invalid input
    or exceptions.
    """
    try:
        # accept a file path (string or PathLike)
        if isinstance(df, (str, os.PathLike, Path)):
            try:
                df = pd.read_csv(str(df))
            except Exception:
                return "Error"

        # basic validation
        if df is None or not hasattr(df, "columns"):
            return "Error"

        cols = set(str(c).lower() for c in df.columns.tolist())

        # check IDENTIFICATORS (case-insensitive): return first matching key
        for key, req_cols in IDENTIFICATORS.items():
            req_lower = set(str(c).lower() for c in req_cols)
            if req_lower.issubset(cols):
                return key

        # bracken detection: rows 2..end -> skip first data row
        if df.shape[0] <= 1:
            return "unknown"

        sample = df.iloc[1:1 + 20]
        flat = pd.Series(sample.values.ravel())

        # consider only non-empty values; convert to numeric coercing errors
        converted = pd.to_numeric(flat, errors="coerce")
        non_empty = ~flat.isna() & (flat.astype(str).str.strip() != "")
        non_numeric = non_empty & converted.isna()

        if not non_numeric.any():
            return "bracken"

        return "unknown"
    except Exception:
        return "Error"
