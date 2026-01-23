"""Curator helper utilities.

This module provides small, well-documented helpers to:
- load a file into a pandas DataFrame,
- run a sequence of processing steps (placeholders for your other processes),
- rotate the original file to a backup name with suffix '_(original)', and
- write the processed DataFrame back using the original filename.

The functions are intentionally minimal and documented so you can
hook in existing processes (pass them to `process_dataframe`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable, List, Optional

import pandas as pd

# Import the medicines fixer from the Curation package so we can call it
# by default when performing curation.
from .fixMedicines import main as fix_medicines_main


def load_file_to_df(path: str | Path) -> pd.DataFrame:
    """Load the CSV at `path` into a pandas DataFrame.

    This uses `pd.read_csv` and returns the DataFrame. If the file does
    not exist a `FileNotFoundError` will be raised.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    # Read as strings by default to avoid unexpected type coercion; callers
    # can convert types later in their processors.
    return pd.read_csv(p, dtype=str)


def process_dataframe(df: pd.DataFrame, processors: Optional[Iterable[Callable[[pd.DataFrame], pd.DataFrame]]]) -> pd.DataFrame:
    """Run a sequence of processor callables against `df`.

    Each processor receives the DataFrame and must return a DataFrame.
    This is a lightweight orchestration layer so you can pass in your
    existing transformation functions.
    """
    if not processors:
        return df

    current = df
    for proc in processors:
        # processors are expected to be pure-style functions: take df -> return df
        current = proc(current)
    return current


def rotate_original(path: str | Path) -> Path:
    """Rename the original file to have suffix '_(original)' before extension.

    If `data.csv` exists, it will be renamed to `data_(original).csv`.
    If the target already exists it will append a numeric suffix to avoid
    clobbering (e.g. `data_(original)_1.csv`). The function returns the
    Path to which the original was renamed.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    stem = p.stem
    suffix = p.suffix
    parent = p.parent
    candidate = parent / f"{stem}_(original){suffix}"
    idx = 1
    while candidate.exists():
        candidate = parent / f"{stem}_(original)_{idx}{suffix}"
        idx += 1
    p.rename(candidate)
    return candidate


def save_dataframe(df: pd.DataFrame, path: str | Path) -> None:
    """Save `df` to `path` as CSV (no index column).

    This will create/overwrite the file at `path`.
    """
    p = Path(path)
    df.to_csv(p, index=False)


def process_file(path: str | Path, processors: Optional[Iterable[Callable[[pd.DataFrame], pd.DataFrame]]] = None):
    """High-level helper that loads, processes, rotates original and saves.

    Steps performed:
    1. Load original CSV into DataFrame.
    2. Call `process_dataframe` with the provided `processors`.
    3. Rename the original file to have '_(original)' suffix.
    4. Save the processed DataFrame back to the original filename.

    `processors` should be an iterable of callables `df -> df` and can
    be used to hook in the processing pipeline (for example, call
    `fixMedicines.fix_medicines_file` or other transformations).
    """
    p = Path(path)
    # Load
    df = load_file_to_df(p)

    # Process (hooks). If no processors provided, call the medicines fixer.
    if processors is None:
        processors = [fix_medicines_main]

    df_processed = process_dataframe(df, processors)

    # Rotate original file
    rotate_original(p)

    # Save processed df using the original filename
    save_dataframe(df_processed, p)


if __name__ == "__main__":
    # Example usage: `python curation.py path/to/patients.csv`
    import sys

    if len(sys.argv) < 2:
        print("Usage: python curation.py path/to/patients.csv")
        raise SystemExit(1)

    target = sys.argv[1]
    # No processors passed here; in real use pass a list of callables.
    process_file(target, processors=None)
