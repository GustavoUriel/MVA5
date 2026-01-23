from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, Union, Iterable

import pandas as pd

from app.scripts.files import findFileType
from metadata.COLUMNS import COLUMNS, IDENTIFICATORS, MEDICINES
from app.modules.dataCuration.fixRemoveInvalidRows import remove_invalid_rows
from app.modules.dataCuration.fixRemoveInvalidValues import remove_invalid_values
from app.modules.dataCuration.fixMedicines import fix_medicines_df
from app.modules.dataCuration.fixNormalizeColumnsNames import normalize_columns, rename_to_canonical


def _fix_medicines_step(df: pd.DataFrame, file_type: Optional[str]) -> Tuple[pd.DataFrame, str]:
    if file_type != "patients":
        return df, "fix_medicines_skipped_not_patients"
    try:
        df_fixed = fix_medicines_df(df)
        return df_fixed, "success_fix_medicines"
    except Exception as e:
        return df, f"fix_medicines_error:{e}"


# remove_invalid_values moved to app/modules/dataCuration/fixRemoveInvalidValues.py


def curate(input_data: Union[str, Path, pd.DataFrame]) -> Tuple[Optional[pd.DataFrame], str]:
    """Main pipeline.

    - Accepts a pandas DataFrame or a file path.
    - If a path is given it is read into a DataFrame.
    - Uses `findFileType` to detect the file type; if it returns
        'Error' or 'unknown' the function returns (None, that_string).
    - Runs a sequence of steps; each step returns (df, result_str).
    - If input was a DataFrame: returns (df, combined_result_string).
    - If input was a path: moves the original to a "_orig" filename and
        writes the processed DataFrame to the original filename, then
        returns (None, combined_result_string).
    """
    is_path = isinstance(input_data, (str, Path))
    path_obj: Optional[Path] = Path(input_data) if is_path else None


    try:
        if is_path:
            df = pd.read_csv(path_obj)
        else:
            df = input_data.copy()
    except Exception as e:
        return None, f"read_error:{e}"

    # Steps pipeline (each returns df, status)
    results: list[str] = []

    # Step 1: identify file type using the project's helper
    ftype = findFileType(df)
    results.append("Type:" + ftype)
    if ftype in ("Error", "unknown"):
        return None, ftype

    # 1) normalize columns
    df = normalize_columns(df, ftype)
    results.append("normalized_columns")

    # 2) remove invalid rows
    # 1b) rename to canonical names where possible
    try:
        df, mapping = rename_to_canonical(df, ftype)
        results.append("renamed_to_canonical")
    except Exception:
        results.append("renamed_to_canonical_failed")

    # 2) remove invalid rows
    df, res = remove_invalid_rows(df, ftype)
    results.append(res)

    # 3) fix medicines (uses existing module)
    df, res = _fix_medicines_step(df, ftype)
    results.append(res)

    # 4) remove invalid values
    df = remove_invalid_values(df)
    results.append("removed_invalid_values")

    result_summary = ";".join(results)

    if is_path and path_obj is not None:
        try:
            src = path_obj
            backup = src.with_name(src.stem + "_orig" + src.suffix)
            if not backup.exists():
                src.replace(backup)
            else:
                # if backup exists, add numeric suffix
                i = 1
                while True:
                    cand = src.with_name(f"{src.stem}_orig_{i}" + src.suffix)
                    if not cand.exists():
                        src.replace(cand)
                        break
                    i += 1
            # write processed dataframe to original filename
            df.to_csv(path_obj, index=False)
        except Exception as e:
            return None, f"save_error:{e}"
        return None, result_summary

    return df, result_summary



__all__ = ["curate"]
