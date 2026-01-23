from __future__ import annotations

from typing import Optional, Tuple

import pandas as pd

from metadata.COLUMNS import REQUIRED


def remove_invalid_rows(df: pd.DataFrame, file_type: Optional[str]) -> Tuple[pd.DataFrame, str]:
    """Remove rows that appear invalid for the detected file type.

    Strategy:
    - For a type with identifier columns in REQUIRED, drop rows where
        all identifier columns are empty/missing.
    - Otherwise return the DataFrame unchanged with a status token.
    """
    if not file_type or file_type not in REQUIRED:
        return df, "no_invalid_row_removal"

    id_cols = [c for c in REQUIRED[file_type] if c in df.columns or c.lower() in df.columns]
    cols_lower = {c.lower(): c for c in df.columns}
    id_cols_actual = []
    for c in id_cols:
        if c in df.columns:
            id_cols_actual.append(c)
        elif c.lower() in cols_lower:
            id_cols_actual.append(cols_lower[c.lower()])

    if not id_cols_actual:
        return df, "no_identifier_columns_found"

    mask_all_empty = df[id_cols_actual].fillna("").astype(str).apply(lambda r: all(not v.strip() for v in r), axis=1)
    df2 = df.loc[~mask_all_empty].copy()
    return df2, f"removed_rows={int(mask_all_empty.sum())}"


__all__ = ["remove_invalid_rows"]
