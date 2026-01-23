from __future__ import annotations

import pandas as pd
from typing import Any, Dict, Tuple

import re
from collections import defaultdict

from metadata.COLUMNS import COLUMNS

def normalize_columns(df: pd.DataFrame, data_type: str) -> pd.DataFrame:
    """Normalize column names to lowercase_snake_case."""

    def _normalize_name(x: Any) -> str:
        s = str(x).strip().replace("\u00A0", " ")
        s = s.lower()
        s = re.sub(r"[\s\-]+", "_", s)
        s = re.sub(r"[^0-9a-z_]+", "_", s)
        s = re.sub(r"_+", "_", s)
        return s.strip("_") or "column"
    
    df = df.copy()
    # normalize column names
    normalized = [_normalize_name(c) for c in df.columns]
    # ensure uniqueness by appending a counter for duplicate names
    counts: Dict[str, int] = {}
    unique_cols: list[str] = []
    for name in normalized:
        if not name:
            name = "column"
        cnt = counts.get(name, 0)
        unique_name = name if cnt == 0 else f"{name}_{cnt}"
        counts[name] = cnt + 1
        unique_cols.append(unique_name)
    df.columns = unique_cols
    
    """Rename columns to canonical names defined in metadata.COLUMNS.COLUMNS[data_type].

    - Normalizes each existing column name using the same rules as
        `normalize_columns`.
    - If an exact normalized match to a canonical name is found, the
        column is renamed to that canonical name.
    - Unmatched columns are replaced by their normalized name.
    - If multiple input columns map to the same target name, numeric
        suffixes (_2, _3, ...) are appended to make names unique.

    Returns (df_renamed, mapping_dict) where mapping_dict maps original
    column name -> new column name.
    """
    canonical = COLUMNS.get(data_type, [])

    canon_norm = { _normalize_name(c): c for c in canonical }

    mapping = {}
    used_counts = defaultdict(int)
    for col in df.columns:
        norm = _normalize_name(col)
        if norm in canon_norm:
            target = canon_norm[norm]
        else:
            target = norm
        used_counts[target] += 1
        mapping[col] = target if used_counts[target] == 1 else f"{target}_{used_counts[target]}"

    df2 = df.rename(columns=mapping)
    return df2


__all__ = ["normalize_columns"]
