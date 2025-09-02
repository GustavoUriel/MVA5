from flask import Flask, jsonify, render_template, send_from_directory, request
import pandas as pd
import re
import os

#@app.route("/api/patients")
def api_table_data(data_path):
  # return data with the same unique column names used by the schema
  full = pd.read_csv(data_path)
  # deduplicate & sanitize columns the same way build_schema does
  cols = list(full.columns)

  def sanitize_base(name):
    return re.sub(r"[^0-9a-zA-Z_]", '_', name)

  seen = {}
  fields = []
  for c in cols:
    base = sanitize_base(c)
    if base in seen:
      seen[base] += 1
      new = f"{base}__{seen[base]}"
    else:
      seen[base] = 0
      new = base
    fields.append(new)
  full.columns = fields
  # replace NaN with None for clean JSON
  # convert to list of plain Python records and replace any missing values with None
  records = full.to_dict(orient="records")
  # sanitize values (convert numpy types and NaN to None)
  
  # Clean the records by replacing NaN values with None
  cleaned_records = []
  for record in records:
    cleaned_record = {}
    for key, value in record.items():
      if pd.isna(value):
        cleaned_record[key] = None
      elif isinstance(value, (int, float)):
        # Convert numpy types to Python types
        cleaned_record[key] = float(value) if isinstance(value, float) else int(value)
      else:
        cleaned_record[key] = str(value) if value is not None else None
    cleaned_records.append(cleaned_record)
  
  return cleaned_records


def api_schema(sample_rows=200, visible_limit=20, data_path=None):
  """Build a simple schema from the CSV header and a small sample of rows.

  - Fields are created from CSV column names. If the same column name appears
    multiple times, a numeric suffix is added to make fields unique.
  - First `visible_limit` columns are visible by default, the rest are hidden.
  - Numeric-looking columns get numeric sorter/headerFilter.
  - Any column name containing "id" is given an initial ascending sort and a
    hyperlink template that searches the value on Google (changeable).
  """
  import colorsys
  import pandas as pd
  import re

  if data_path is None:
    data_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'patients.csv')
  df = pd.read_csv(data_path, nrows=sample_rows)
  orig_cols = list(df.columns)

  # sanitize base names (remove dots and non-word chars) then deduplicate
  def sanitize_base(name):
    base = re.sub(r"[^0-9a-zA-Z_]", '_', name)
    # avoid leading digits-only names causing weirdness
    return base

  seen = {}
  fields = []
  for c in orig_cols:
    base = sanitize_base(c)
    if base in seen:
      seen[base] += 1
      new = f"{base}__{seen[base]}"
    else:
      seen[base] = 0
      new = base
    fields.append(new)
  # rename dataframe columns to unique, sanitized names
  df.columns = fields

  schema_cols = []

  # generate a small, stable pastel palette for categorical labels (0,1,2)

  def pastel_hex_for_index(i, total=3):
    # 0: green, 1: red, 2: blue (light pastel versions)
    pastel_colors = {
        0: "#6aee61",  # light green
        1: "#fa7e7e",  # light red
        2: "#4790f7",  # light blue
    }
    return pastel_colors.get(i, '#cccccc')

  GLOBAL_LABEL_COLORS_012 = {
      i: pastel_hex_for_index(i, total=3) for i in (0, 1, 2)}

  for i, f in enumerate(fields):
    # label should reflect the original header (use that if possible)
    orig = orig_cols[i]
    label = orig.replace('_', ' ').replace('.', ' ').title()
    label = orig
    hidden = False if i < visible_limit else True
    col = {
        "field": f,
        "label": label,
        "sortable": True,
        "hidden": hidden,
        "headerFilter": True,
        "editable": True,
    }

    # heuristic: if column name contains '_id', start sorted by it
    if '_id' in f.lower():
      col['sort'] = 'asc'

    # heuristic: if column name contains '_id', makes it not editable
    if '_id' in f.lower():
      col['editable'] = False
    else:
      col['editable'] = True

    # heuristic: if column name contains 'ethnicity', add initial sort and hyperlink
    if 'ethnicity' in f.lower():
      # open a Google search for the value; change to a local detail route if desired
      col['hyperlink'] = 'https://www.google.com/search?q={value}'

    # If column is numeric and only contains 0, 1, 2, use displayStyle with labels/colors
    try:

      # DEBUG: verify underlying value types and whether they are numeric strings
      raw_nonnull = df[f].dropna()
      sample_types = list({type(x).__name__ for x in raw_nonnull.head(20)})
      # attempt coercion to numeric to detect numeric strings
      coerced = pd.to_numeric(raw_nonnull, errors='coerce')
      numeric_count = int(coerced.notna().sum())
      total_count = int(len(raw_nonnull))
      numeric_ratio = (numeric_count / total_count) if total_count else 0
      print(f"[SCHEMA DEBUG] field={f!r} pandas_dtype={df[f].dtype} sample_types={sample_types} "
            f"numeric_ratio={numeric_ratio:.2f} ({numeric_count}/{total_count})")
      # optional: expose the debug info to the client for inspection
      # col['_debug_valueType'] = {
      # 'pandas_dtype': str(df[f].dtype),
      # 'sample_types': sample_types,
      # 'numeric_ratio': numeric_ratio,
      # }

      vals = pd.to_numeric(df[f], errors='coerce').dropna()
      if not vals.empty and (vals % 1 == 0).all():
        unique_ints = set(vals.astype(int).unique())
        if unique_ints.issubset({0, 1, 2}) and len(unique_ints) > 0:
          col['displayType'] = 'label'
          col['colorScheme'] = 'custom'

          # always emit the full stable mapping for 0,1,2 (string keys)
          # so the same numeric value maps to the same pastel color across columns
          col['customColors'] = {
              str(k): GLOBAL_LABEL_COLORS_012[k] for k in (0, 1, 2)}
    except Exception:
      pass

    # infer numeric vs string for better sorting/filter behavior
    try:
      dtype = pd.api.types.infer_dtype(df[f], skipna=True)
    except Exception:
      dtype = 'string'

    if dtype in ('integer', 'floating', 'mixed-integer-float'):
      col['sorter'] = 'number'
      col['headerFilter'] = 'number'

      # Check if this column would benefit from progress bar display
      # Look for columns that might represent percentages, scores, or bounded values
      col_name_lower = f.lower()
      if any(keyword in col_name_lower for keyword in ['percent', 'percentage', 'score', 'rate', 'ratio', 'level', 'bmi', 'iss', 'riss']):
        # Calculate min/max for progress bar
        try:
          numeric_values = pd.to_numeric(df[f], errors='coerce').dropna()
          if len(numeric_values) > 0:
            col_min = float(numeric_values.min())
            col_max = float(numeric_values.max())
            # Only use progress bar if we have a reasonable range
            if col_max > col_min and (col_max - col_min) > 0 and numeric_values.nunique() > 5:
              col['displayType'] = 'progressBar'
              col['min'] = col_min
              col['max'] = col_max
        except Exception:
          pass
    else:
      col['sorter'] = 'string'
      col['headerFilter'] = 'input'

    schema_cols.append(col)

  return {"columns": schema_cols}


