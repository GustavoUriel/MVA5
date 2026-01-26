from __future__ import annotations

import pandas as pd
from typing import Optional
import re
from difflib import SequenceMatcher
from collections import defaultdict

from metadata.COLUMNS import COLUMNS


def _fuzzy_match_score(s1: str, s2: str) -> float:
    """Calculate similarity score between two strings using SequenceMatcher."""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()


def _find_best_match(column_name: str, canonical_names: list[str], threshold: float = 0.6) -> Optional[str]:
    """Find the best matching canonical column name using fuzzy matching."""
    best_match = None
    best_score = 0.0
    
    for canon_name in canonical_names:
        score = _fuzzy_match_score(column_name, canon_name)
        if score > best_score:
            best_score = score
            best_match = canon_name
    
    return best_match if best_score >= threshold else None


def _clean_date_column_name(col_name: str) -> str:
    """Remove _ and numerals and _eng after start_date or end_date."""
    # Pattern to match start_date or end_date at the beginning, followed by optional suffixes
    # Examples: start_date, start_date_1, start_date_eng, start_date_eng_1, start_dateeng_1
    col_lower = col_name.lower()
    # Match start_date or end_date at the beginning
    pattern = r'^(start_date|end_date)'
    match = re.match(pattern, col_lower)
    if match:
        base_name = match.group(1)  # 'start_date' or 'end_date'
        # Check if there are any suffixes to remove (_eng, _1, _eng_1, etc.)
        remaining = col_lower[len(base_name):]
        # If there's anything after the base name, it's a suffix to remove
        if remaining:
            return base_name
        return base_name
    return col_name


def match_column_names(df: pd.DataFrame, file_type: Optional[str]) -> pd.DataFrame:
    """Match dataset column names with canonical names using fuzzy matching.
    
    - If file_type is 'bracken', returns df unmodified.
    - Uses fuzzy matching to match dataset columns to canonical columns from COLUMNS.
    - Only allows repeated column names for 'start_date' and 'end_date'.
    - For patients datasets, cleans start_date and end_date column names by removing
      _ and numerals and _eng suffixes.
    
    Args:
        df: DataFrame with columns to match
        file_type: Type of dataset ('patients', 'taxonomy', 'bracken', etc.)
    
    Returns:
        DataFrame with matched column names
    """
    # Skip for bracken datasets
    if file_type == "bracken":
        return df
    
    # Get canonical column names for this file type
    canonical_names = COLUMNS.get(file_type, [])
    if not canonical_names:
        return df
    
    df = df.copy()
    mapping = {}
    used_counts = defaultdict(int)
    
    # Special columns that are allowed to be duplicated
    allowed_duplicates = {'start_date', 'end_date'}
    
    for col in df.columns:
        # Find best fuzzy match
        best_match = _find_best_match(str(col), canonical_names)
        
        if best_match:
            target = best_match
        else:
            # No good match found, keep original column name
            target = str(col)
        
        # For patients datasets, clean start_date and end_date column names
        # Check if the target matches the pattern (e.g., Start_Date_1, Start_DateEng, etc.)
        if file_type == "patients":
            cleaned = _clean_date_column_name(target)
            # If cleaning changed the name, it means it matched the pattern
            if cleaned.lower() != target.lower():
                target = cleaned
        
        # Handle duplicates: only allow duplicates for start_date and end_date
        if target.lower() in allowed_duplicates:
            # Allow duplicates, append counter if needed
            used_counts[target] += 1
            final_name = target if used_counts[target] == 1 else f"{target}_{used_counts[target]}"
        else:
            # For other columns, ensure uniqueness
            if used_counts[target] > 0:
                # Column already used, append counter
                used_counts[target] += 1
                final_name = f"{target}_{used_counts[target]}"
            else:
                used_counts[target] = 1
                final_name = target
        
        mapping[col] = final_name
    
    df_renamed = df.rename(columns=mapping)
    return df_renamed


__all__ = ["match_column_names"]
