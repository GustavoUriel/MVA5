''' Description for IA:

Create an api endpoint that uses the functions in this file




@app.route("/api/table/data")
def api_table():
  return jsonify(build_table_data(csv_file=DATA_PATH))


@app.route("/api/table/schema")
def api_table_schema():
  return jsonify(build_schema(csv_file=DATA_PATH))


@app.route("/api/table/save", methods=['POST'])
def save(csv_file=DATA_PATH):
  try:
    data = request.get_json()
    if not data:
      return jsonify({"status": "error", "message": "No data received"}), 400
    save_table(data=data, csv_file=csv_file)
    return jsonify({"status": "success", "message": "Data saved successfully"}), 200
  except Exception as e:
    print(f"Error processing request: {str(e)}")
    return jsonify({"status": "error", "message": f"Error processing request: {str(e)}"}), 500

'''


import colorsys
from flask import jsonify
import pandas as pd
import re
import json


def build_table_data(csv_file):
  """Read CSV and return sanitized list of records suitable for JSON response.

  Mirrors the column sanitization used by build_schema so field names match.
  """

  if csv_file is None:
    return []

  full = pd.read_csv(csv_file)
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

  # convert to list of plain Python records and replace any missing values with None
  records = full.to_dict(orient="records")

  def sanitize_value(v):
    try:
      if pd.isna(v):
        return None
    except Exception:
      pass
    # convert numpy types to native python
    if hasattr(v, 'item'):
      try:
        return v.item()
      except Exception:
        return v
    return v

  sanitized = []
  for r in records:
    nr = {k: sanitize_value(v) for k, v in r.items()}
    sanitized.append(nr)

  return sanitized


def build_schema(sample_rows=200, visible_limit=12, csv_file=None):
  """Build a simple schema from the CSV header and a small sample of rows.

  - Fields are created from CSV column names. If the same column name appears
    multiple times, a numeric suffix is added to make fields unique.
  - First `visible_limit` columns are visible by default, the rest are hidden.
  - Numeric-looking columns get numeric sorter/headerFilter.
  - Any column name containing "id" is given an initial ascending sort and a
    hyperlink template that searches the value on Google (changeable).
  """
  if csv_file is None:
    return []

  df = pd.read_csv(csv_file, nrows=sample_rows)
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


def save_table(data=None, csv_file=None):
  # Save modified data (filtered and edited) to a new CSV file
  try:
    if not data:
      return jsonify({"status": "error", "message": "No data received"}), 400
    if not csv_file:
      return jsonify({"status": "error", "message": "No csv_file name received"}), 400

    modified_data = data.get('data', [])
    has_changes = data.get('hasChanges', False)
    change_log = data.get('changeLog', [])
    timestamp = data.get('timestamp', '')

    # ✅ PRESERVE COLUMN ORDER: Get column order from the first data row
    column_order = list(modified_data[0].keys())

    # Convert back to DataFrame with preserved column order
    df = pd.DataFrame(modified_data, columns=column_order)

    # Create a timestamp for the filename and preserve original CSV name when possible
    from datetime import datetime
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Attempt to derive original filename from a module-level known path if available
    try:
      # fall back to a sensible default if not set
      orig_path = csv_file
      import os as _os
      orig_dir, orig_file = _os.path.split(orig_path)
      base, ext = _os.path.splitext(orig_file)
    except Exception:
      return jsonify({"status": "error", "message": "Bad csv_file name/path received"}), 400

#    output_filename = _os.path.join(
#        orig_dir, f"{base} mod {timestamp_str}{ext}")
    output_filename = orig_path

    # ✅ SAVE WITH PRESERVED COLUMN ORDER
    df.to_csv(output_filename, index=False, columns=column_order)

    return jsonify({
        "status": "success",
        "message": f"Successfully saved {len(df)} records",
        "filename": output_filename,
        "total_records": len(df),
        "has_changes": has_changes,
        "total_changes": len(change_log),
        "timestamp": timestamp,
        "saved_at": datetime.now().isoformat()
    })

  except Exception as e:
    print(f"Error saving table data: {str(e)}")  # For debugging
    return jsonify({
        "status": "error",
        "message": f"Failed to save data: {str(e)}"
    }), 500
