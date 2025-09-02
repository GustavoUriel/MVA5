/*  Smart Table - Enhanced Reusable Table Component with Embedded CSS
  
  A complete, self-contained table component with advanced features:
  - Responsive Bootstrap-styled design
  - Smart column filtering (text, numeric, select)
  - Dual pagination (top and bottom)
  - Column visibility controls
  - Row deletion with confirmation
  - Data export (CSV)
  - Refresh functionality
  - Filter clearing
  - Mobile-responsive design
  
  Dependencies:
  - Tabulator.js (https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js)
  - Bootstrap 5.3+ CSS and JS
  - Bootstrap Icons (optional, for better UX)
  
  Usage:
  1. Include this file in your project
  2. Call: createTableComponent('#container', '/api/endpoint', options)
  
  Example:
  createTableComponent('#my-table', '/api/this_table', {
    pageSize: 25,
    filename: 'this_table_export',
    storageKey: 'my_table_filters',
    showDebug: false,
    columnConfig: {
      'status': { 
        displayType: 'label',
        colorScheme: 'auto' // or 'status', 'priority', etc.
      },
      'progress_score': { 
        displayType: 'progressBar',
        progressConfig: {
          showText: true,
          barColor: 'primary',
          height: '20px'
        }
      },
      'category': {
        displayType: 'label',
        colorScheme: 'custom',
        customColors: {
          'urgent': '#dc3545',
          'normal': '#28a745',
          'low': '#6c757d'
        }
      }
    }
  });
  
  API Requirements:
  - GET /api/endpoint -> returns array of data objects
  - GET /api/endpoint/schema -> returns {columns: [...]} with column definitions
  
  @param {string|Element} containerSelector - CSS selector or DOM element
  @param {string} apiBase - Base API endpoint URL
  @param {Object} options - Configuration options
  @returns {Object} Component API with table instance and methods
*/

/* THIS IS THE HTML INJECTION POINT FOR THE TABLE COMPONENT
<div id="this_table-component"></div>
*/

/* THIS IS THE JSCRIPT CODE TO CALL FOR THE TABLE COMPONENT

createTableComponent('#this_table-component', '/api/this_table', {
  showDebug: true, // Set to false in production
  pageSize: 30,
  filename: 'this_table_export',
  columnConfig: {
      // Example: Gender with custom colors
      'gender': {
          displayType: 'label',
          colorScheme: 'custom',
          customColors: {
              'Male': '#007bff',
              'Female': '#e83e8c',
              'Other': '#6c757d'
          }
      }
  }
});

*/


/* THIS IS THE PYTHON CODE FOR THE API ENDPOINT FOR THE DATA FOR THE TABLE 
@app.route("/api/this_table")
def api_this_table():
  # return data with the same unique column names used by the schema
  full = pd.read_csv(DATA_PATH)
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

  return jsonify(sanitized)

*/

/* THIS IS THE PYTHON CODE TO DINAMICALLY BUILD THE SCHEMA AND ENDPOINTS:

@app.route("/api/this_table/schema")
def api_this_table_schema():
  return jsonify(build_schema())


def build_schema(sample_rows=200, visible_limit=12):
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

  df = pd.read_csv(DATA_PATH, nrows=sample_rows)
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
*/

/* THIS IS THE PYTHON CODE FOR API ENDPOINT TO RECEIVE THE MODIFIED DATASET FROM TABLE. 
@app.route("/api/this_table/save", methods=['POST'])
def save_this_table():
  """
  Save modified patient data (filtered and edited) to a new CSV file
  """
  try:
    data = request.get_json()
    if not data:
      return jsonify({"status": "error", "message": "No data received"}), 400

    modified_data = data.get('data', [])
    has_changes = data.get('hasChanges', False)
    change_log = data.get('changeLog', [])
    timestamp = data.get('timestamp', '')

    if not modified_data:
      return jsonify({"status": "error", "message": "No patient data to save"}), 400

    # Convert back to DataFrame
    df = pd.DataFrame(modified_data)

    # Create a timestamp for the filename
    from datetime import datetime
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save to new CSV file with timestamp
    output_filename = f'this_table_modified_{timestamp_str}.csv'
    df.to_csv(output_filename, index=False)

    # Also save change log if there are changes
    if has_changes and change_log:
      change_log_filename = f'this_table_changes_{timestamp_str}.json'
      import json
      with open(change_log_filename, 'w') as f:
        json.dump({
            'changes': change_log,
            'total_changes': len(change_log),
            'timestamp': timestamp,
            'saved_at': datetime.now().isoformat()
        }, f, indent=2)

    return jsonify({
        "status": "success",
        "message": f"Successfully saved {len(df)} records",
        "filename": output_filename,
        "total_records": len(df),
        "has_changes": has_changes,
        "total_changes": len(change_log),
        "change_log_file": f'this_table_changes_{timestamp_str}.json' if has_changes else None,
        "timestamp": timestamp,
        "saved_at": datetime.now().isoformat()
    })

  except Exception as e:
    print(f"Error saving this_table data: {str(e)}")  # For debugging
    return jsonify({
        "status": "error",
        "message": f"Failed to save data: {str(e)}"
    }), 500

*/



// Inject CSS styles - only once per page
(function injectSmartTableStyles() {
  if (document.getElementById('smart-table-styles')) return; // Already injected
  
  const css = `
/* Enhanced styles for the reusable table component */

/* Component Controls */
.tc-controls { 
    margin: 12px 0; 
    padding: 12px;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 0.5rem;
    border: 1px solid #dee2e6;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.tc-table { 
    margin-top: 16px; 
}

.tc-debug { 
    margin: 16px 0; 
    padding: 12px; 
    border: 1px solid #dee2e6; 
    border-radius: 0.375rem;
    max-height: 250px; 
    overflow: auto; 
    font-size: 12px; 
    background: #f8f9fa;
    font-family: 'Courier New', monospace;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}

/* Enhanced Dropdown Styles */
.dropdown-menu .form-check-input { 
    vertical-align: middle;
    margin-top: 0;
}

.dropdown-menu { 
    max-height: 300px; 
    overflow: auto;
    border-radius: 0.5rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    border: 1px solid #dee2e6;
}

.dropdown-item {
    padding: 8px 16px;
    border-radius: 0.25rem;
    margin: 2px 4px;
    transition: all 0.2s ease;
}

.dropdown-item:hover {
    background-color: #e7f3ff;
    color: #0d6efd;
}

/* Enhanced Tabulator Styling */
.tabulator {
    border: 1px solid #dee2e6;
    border-radius: 0.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    overflow: hidden;
    background: white;
    /* Make table text non-selectable to prevent confusion */
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}

.tabulator .tabulator-header {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-bottom: 2px solid #dee2e6;
    color: #212529;
}

.tabulator .tabulator-col {
    background: transparent;
    border-right: 1px solid rgba(0,0,0,0.1);
}

.tabulator .tabulator-col:last-child {
    border-right: none;
}

.tabulator .tabulator-col .tabulator-col-title {
    font-weight: 700;
    color: #212529;
    font-size: 14px;
    letter-spacing: 0.5px;
    text-shadow: none;
}

.tabulator .tabulator-col-sorter {
    color: #495057 !important;
    text-shadow: none;
}

.tabulator .tabulator-col[aria-sort="asc"] .tabulator-col-content {
    background: rgba(13, 110, 253, 0.1);
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}

.tabulator .tabulator-col[aria-sort="desc"] .tabulator-col-content {
    background: rgba(13, 110, 253, 0.1);
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}

/* Row Styling */
.tabulator .tabulator-row {
    border-bottom: 1px solid #e9ecef;
    transition: all 0.2s ease;
}

.tabulator .tabulator-row:nth-child(even) {
    background-color: #fafbfc;
}

.tabulator .tabulator-row:hover {
    background: linear-gradient(135deg, #e7f3ff 0%, #cce7ff 100%);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.tabulator .tabulator-row.tabulator-selected {
    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    border-left: 4px solid #0d6efd;
}

/* Cell Styling */
.tabulator .tabulator-cell {
  padding: 10px 14px;
  border-right: 1px solid #f1f3f4;
  vertical-align: middle;
  font-size: 0.95rem; /* slightly larger cell text for better readability */
}

.tabulator .tabulator-cell:last-child {
    border-right: none;
}

/* Enhanced Filter Inputs */
.tabulator .tabulator-header-filter input,
.tabulator .tabulator-header-filter select {
    border-radius: 0.25rem;
    border: 1px solid #ced4da;
    padding: 4px 8px;
    font-size: 12px;
    transition: all 0.2s ease;
}

.tabulator .tabulator-header-filter input:focus,
.tabulator .tabulator-header-filter select:focus {
    border-color: #0d6efd;
    box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
    outline: 0;
}

/* Button Enhancements */
.btn {
    transition: all 0.2s ease;
    font-weight: 500;
    border-radius: 0.375rem;
}

.btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.tc-row-del {
    transition: all 0.2s ease;
    border-radius: 50% !important;
    width: 24px;
    height: 24px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
}

.tc-row-del:hover {
    background-color: #dc3545;
    border-color: #dc3545;
    color: white;
    transform: scale(1.1);
}

/* Card Enhancements */
.card {
    border-radius: 0.75rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    border: 1px solid #e3e6ea;
    overflow: hidden;
}

.card-header {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-bottom: 2px solid #dee2e6;
    padding: 16px 20px;
}

.card-body {
    padding: 0;
}

.card-footer {
    background: #f8f9fa;
    border-top: 1px solid #dee2e6;
    padding: 12px 20px;
}

/* Responsive Design */
@media (max-width: 768px) {
    .tc-controls {
        flex-direction: column;
        gap: 8px;
    }
    
    .tc-controls .d-flex {
        flex-direction: column;
        width: 100%;
    }
    
    .tc-controls .btn {
        width: 100%;
        margin-bottom: 8px;
    }
    
    .tabulator .tabulator-cell {
        padding: 6px 8px;
        font-size: 14px;
    }
    
    .tc-debug {
        font-size: 11px;
        max-height: 150px;
    }
}

/* Loading Animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.card {
    animation: fadeIn 0.5s ease-out;
}

/* Accessibility Improvements */
.btn:focus {
    box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.5);
}

.tc-row-del:focus {
    box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.5);
}

/* Scrollbar Styling */
.tc-debug::-webkit-scrollbar,
.dropdown-menu::-webkit-scrollbar {
    width: 8px;
}

.tc-debug::-webkit-scrollbar-track,
.dropdown-menu::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.tc-debug::-webkit-scrollbar-thumb,
.dropdown-menu::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
}

.tc-debug::-webkit-scrollbar-thumb:hover,
.dropdown-menu::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}

/* Combo Editor Styles */
.position-relative .dropdown-menu {
    border: 1px solid #ced4da;
    border-radius: 4px;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    margin-top: 2px;
    font-size: 12px;
}

.position-relative .dropdown-item {
    cursor: pointer;
    transition: background-color 0.15s ease-in-out;
    padding: 6px 12px;
}

.position-relative .dropdown-item:hover {
    background-color: #f8f9fa;
}

.position-relative .dropdown-item:focus,
.position-relative .dropdown-item:active {
    background-color: #007bff;
    color: white;
}

.position-relative .dropdown-item .badge {
    opacity: 0.8;
    font-size: 10px;
}

.position-relative .dropdown-item:hover .badge {
    opacity: 1;
}

/* Spinning animation for refresh button */
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.spin {
    animation: spin 1s linear infinite;
}

/* Enhanced table info styling */
#table-info {
    background: rgba(13, 110, 253, 0.1);
    padding: 4px 8px;
    border-radius: 0.25rem;
    border: 1px solid rgba(13, 110, 253, 0.2);
}

/* Loading states */
.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* Success state animations */
@keyframes checkmark {
    0% { transform: scale(0.8); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

.btn-success i.bi-check-circle {
    animation: checkmark 0.3s ease-out;
}

/* Clear filters button styling */
.btn-outline-warning {
    border-color: #ffc107;
    color: #ffc107;
}

.btn-outline-warning:hover {
    background-color: #ffc107;
    border-color: #ffc107;
    color: #000;
}

.btn-outline-warning:focus {
    box-shadow: 0 0 0 0.2rem rgba(255, 193, 7, 0.5);
}

.btn-outline-warning:disabled {
    color: #ffc107;
    background-color: transparent;
    border-color: #ffc107;
    opacity: 0.6;
}

/* Enhanced Pagination Styling */
.tc-pager {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 16px;
    padding: 8px 0;
}

.tabulator-paginator {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    max-width: fit-content;
    margin: 0 auto;
}

.tabulator-page-counter {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    color: #1565c0;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid #90caf9;
    box-shadow: 0 2px 4px rgba(21, 101, 192, 0.1);
}

.tabulator-page-size {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #495057;
    font-weight: 500;
}

.tabulator-page-size label {
    margin: 0;
    font-weight: 600;
    color: #6c757d;
}

.tabulator-page-size select {
    border: 2px solid #dee2e6;
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 13px;
    font-weight: 600;
    background: white;
    color: #495057;
    transition: all 0.2s ease;
    cursor: pointer;
}

.tabulator-page-size select:hover {
    border-color: #0d6efd;
    box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.15);
}

.tabulator-page-size select:focus {
    border-color: #0d6efd;
    box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
    outline: 0;
}

.tabulator-pages {
    display: flex;
    align-items: center;
    gap: 4px;
    flex-wrap: wrap;
}

.tabulator-page {
    border: 2px solid #dee2e6;
    background: white;
    color: #495057;
    padding: 8px 12px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 13px;
    transition: all 0.2s ease;
    text-decoration: none;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 36px;
    height: 36px;
}

.tabulator-page:hover {
    background: #e7f3ff;
    border-color: #0d6efd;
    color: #0d6efd;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(13, 110, 253, 0.15);
}

.tabulator-page.active {
    background: linear-gradient(135deg, #0d6efd 0%, #0056b3 100%);
    border-color: #0d6efd;
    color: white;
    box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
    transform: translateY(-1px);
}

.tabulator-page.active:hover {
    background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
    transform: translateY(-1px);
}

.tabulator-page:disabled,
.tabulator-page.disabled {
    background: #f8f9fa;
    border-color: #e9ecef;
    color: #adb5bd;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.tabulator-page:disabled:hover,
.tabulator-page.disabled:hover {
    background: #f8f9fa;
    border-color: #e9ecef;
    color: #adb5bd;
    transform: none;
    box-shadow: none;
}

/* Navigation buttons styling */
.tabulator-page[data-page="first"],
.tabulator-page[data-page="prev"],
.tabulator-page[data-page="next"],
.tabulator-page[data-page="last"] {
    background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
    color: white;
    border-color: #6c757d;
    font-weight: 700;
}

.tabulator-page[data-page="first"]:hover,
.tabulator-page[data-page="prev"]:hover,
.tabulator-page[data-page="next"]:hover,
.tabulator-page[data-page="last"]:hover {
    background: linear-gradient(135deg, #495057 0%, #343a40 100%);
    border-color: #495057;
    color: white;
}

/* Add icons to navigation buttons via CSS content */
.tabulator-page[data-page="first"]::before {
    content: "⏮";
    margin-right: 4px;
}

.tabulator-page[data-page="prev"]::before {
    content: "◀";
    margin-right: 4px;
}

.tabulator-page[data-page="next"]::after {
    content: "▶";
    margin-left: 4px;
}

.tabulator-page[data-page="last"]::after {
    content: "⏭";
    margin-left: 4px;
}

/* Responsive pagination */
@media (max-width: 768px) {
    .tc-pager {
        flex-direction: column;
        gap: 12px;
        text-align: center;
    }
    
    .tabulator-paginator {
        justify-content: center;
        width: 100%;
    }
    
    .tabulator-pages {
        justify-content: center;
        gap: 2px;
    }
    
    .tabulator-page {
        padding: 6px 8px;
        min-width: 32px;
        height: 32px;
        font-size: 12px;
    }
    
    .tabulator-page-counter {
        order: -1;
        width: 100%;
        text-align: center;
    }
}

/* Loading state for pagination */
.tc-pager.loading {
    opacity: 0.6;
    pointer-events: none;
}

.tc-pager.loading::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20px;
    height: 20px;
    margin: -10px 0 0 -10px;
    border: 2px solid #f3f3f3;
    border-top: 2px solid #0d6efd;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

/* Top pagination container styling */
.border-bottom.bg-light {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
    border-bottom: 2px solid #dee2e6 !important;
}

/* Action buttons styling */
.tc-row-select, .tc-row-del {
    border-radius: 3px !important;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Selection button - more compact */
.tc-row-select {
    min-width: 20px;
    height: 20px;
}

/* Delete button - normal size */
.tc-row-del {
    min-width: 24px;
    height: 24px;
}

.tc-row-select:hover {
    background-color: #cfe2ff !important;
    border-color: #0d6efd !important;
}

.tc-row-del:hover {
    background-color: #f8d7da !important;
    border-color: #dc3545 !important;
}

.tc-row-select.selected {
    background-color: #0d6efd !important;
    color: white !important;
    border-color: #0d6efd !important;
}

/* Ensure cells only edit on double-click, not single click */
.tabulator .tabulator-cell {
    cursor: default;
}

.tabulator .tabulator-cell[tabulator-field]:not(.tabulator-editing) {
    pointer-events: auto;
}

 /* Make editable cells visually distinct */
 .tabulator .tabulator-cell[tabulator-field].tabulator-editable {
     cursor: cell;
     transition: background-color 0.2s ease;
 }
 
 .tabulator .tabulator-cell[tabulator-field].tabulator-editable:hover {
     background-color: rgba(13, 110, 253, 0.05) !important;
 }
 
 /* Visual indicator for editable columns when editing is enabled */
 .tabulator .tabulator-cell[tabulator-field].editing-enabled {
     border-left: 3px solid #28a745;
     background-color: rgba(40, 167, 69, 0.02);
 }
 
 .tabulator .tabulator-cell[tabulator-field].editing-enabled:hover {
     background-color: rgba(40, 167, 69, 0.08) !important;
 }
 
 /* Column header editing indicator */
 .tabulator .tabulator-col.editing-enabled {
     background: linear-gradient(135deg, rgba(40, 167, 69, 0.1) 0%, rgba(40, 167, 69, 0.05) 100%) !important;
     border-left: 3px solid #28a745 !important;
 }
 
 .tabulator .tabulator-col.editing-enabled .tabulator-col-title {
     color: #155724 !important;
     font-weight: 800 !important;
 }
 
 /* Table editing mode indicator */
 .card.editing-mode {
     border: 3px solid #28a745 !important;
     box-shadow: 0 0 20px rgba(40, 167, 69, 0.3) !important;
 }
 
 .card.editing-mode .card-header {
     background: linear-gradient(135deg, rgba(40, 167, 69, 0.1) 0%, rgba(40, 167, 69, 0.05) 100%) !important;
     border-bottom: 2px solid #28a745 !important;
 }
 
 .card.editing-mode .card-header::before {
     content: "✏️ EDITING MODE";
     position: absolute;
     top: 8px;
     right: 16px;
     background: #28a745;
     color: white;
     padding: 4px 8px;
     border-radius: 12px;
     font-size: 11px;
     font-weight: bold;
     z-index: 10;
 }

/* Make sure selected rows have proper visual feedback */
.tabulator .tabulator-row.tabulator-selected {
    background-color: rgba(13, 110, 253, 0.1) !important;
    border-left: 3px solid #0d6efd !important;
}
`;

  const style = document.createElement('style');
  style.id = 'smart-table-styles';
  style.textContent = css;
  document.head.appendChild(style);
})();

window.createTableComponent = async function(containerSelector, apiBase, options = {}){
  const container = (typeof containerSelector === 'string') ? document.querySelector(containerSelector) : containerSelector;
  if(!container) throw new Error('Container not found: ' + containerSelector);

  // Configuration defaults
  const config = {
    pageSize: 25,
    filename: 'export',
    storageKey: apiBase,
    showDebug: false,
    columnConfig: {},
    ...options
  };

  // Arrays to store handlers for organized setup
  const columnToggleHandlers = [];
  const debugHandlers = [];
  const paginationHandlers = [];
  
    // Track changes and filtered data
  let hasChanges = false;
  let changeLog = [];
  
     // Track editing state
   let editingEnabled = false;
   
   // Store original editors for each column (separate from column definitions)
   const originalEditors = {};
  
  // Color schemes for label display
  const colorSchemes = {
    status: {
      'active': '#28a745', 'completed': '#007bff', 'pending': '#ffc107', 
      'cancelled': '#dc3545', 'draft': '#6c757d', 'approved': '#20c997'
    },
    priority: {
      'high': '#dc3545', 'medium': '#ffc107', 'low': '#28a745',
      'urgent': '#e83e8c', 'normal': '#007bff', 'minor': '#6c757d'
    },
    category: {
      'a': '#007bff', 'b': '#28a745', 'c': '#ffc107', 'd': '#dc3545',
      'type1': '#e83e8c', 'type2': '#20c997', 'type3': '#fd7e14'
    },
    auto: [
      '#007bff', '#28a745', '#ffc107', '#dc3545', '#e83e8c',
      '#20c997', '#fd7e14', '#6f42c1', '#e91e63', '#00bcd4'
    ]
  };

  // Utility functions for advanced formatting
  function createLabelFormatter(fieldName, columnConfig, uniqueValues) {
    return function(cell) {
      const value = cell.getValue();
      if (value === null || value === undefined || value === '') return '';
      
      const config = columnConfig[fieldName] || {};
      let color = '#6c757d'; // default gray
      
      if (config.colorScheme === 'custom' && config.customColors) {
        color = config.customColors[value] || color;
      } else if (config.colorScheme && colorSchemes[config.colorScheme]) {
        if (Array.isArray(colorSchemes[config.colorScheme])) {
          // Auto color scheme - assign colors based on index
          const index = uniqueValues.indexOf(value) % colorSchemes[config.colorScheme].length;
          color = colorSchemes[config.colorScheme][index];
        } else {
          // Named color scheme
          color = colorSchemes[config.colorScheme][value] || color;
        }
      } else if (uniqueValues.length <= 10) {
        // Auto-assign colors for <= 10 unique values
        const index = uniqueValues.indexOf(value) % colorSchemes.auto.length;
        color = colorSchemes.auto[index];
      }
      
  return `<span class="badge" style="background-color: ${color}; color: white; font-size: 0.9em; padding: 0.35em 0.6em; line-height: 1;">${value}</span>`;
    };
  }


  function createProgressBarFormatter(fieldName, columnConfig, minValue, maxValue) {
    return function(cell) {
      const value = cell.getValue();
      if (value === null || value === undefined || value === '') return '';

      const numValue = parseFloat(value);
      if (isNaN(numValue)) return value;

      const config = (typeof columnConfig === 'object') ? columnConfig : (columnConfig?.[fieldName] ? columnConfig[fieldName].progressConfig || {} : {});
      const min = (typeof minValue === 'number' && !isNaN(minValue)) ? minValue : 0;
      const max = (typeof maxValue === 'number' && !isNaN(maxValue)) ? maxValue : min + 100;
      const span = Math.max(0, Math.min(1, (numValue - min) / (max - min)));
      const percentage = span * 100;

  const barColor = (config && config.progressConfig && config.progressConfig.barColor) || config.barColor || 'primary';
  const height = (config && config.progressConfig && config.progressConfig.height) || config.height || '20px';
  const showText = (config && config.progressConfig && typeof config.progressConfig.showText !== 'undefined') ? config.progressConfig.showText : (typeof config.showText !== 'undefined' ? config.showText : true);

      const bootstrapColors = {
        primary: '#007bff', success: '#28a745', warning: '#ffc107',
        danger: '#dc3545', info: '#17a2b8', secondary: '#6c757d'
      };

      const color = bootstrapColors[barColor] || barColor;

  // Format raw value for display (keep precision for floats)
  const rawText = Number.isInteger(numValue) ? String(numValue) : String(Math.round(numValue * 10) / 10);

      return `
  <div style="width: 100%; background-color: #f3f4f6; border-radius: 4px; height: ${height}; position: relative; overflow: hidden;">
          <div style="width: ${Math.max(0, Math.min(100, percentage))}%; background-color: #99cafcff; height: 100%; border-radius: 4px; transition: width 0.3s ease;"></div>
          ${showText ? `<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; display:flex; align-items:center; justify-content:center; font-size: 0.95em; font-weight: 600; color: ${percentage > 50 ? 'white' : '#495057'};">${rawText}</div>` : ''}
        </div>
      `;
    };
  }

  // Function to create debug section
  function createDebugSection(apiBase) {
    const debugContainer = document.createElement('div');
    debugContainer.className = 'mt-4';
    const debugId = 'debugSection-' + Math.random().toString(36).substr(2, 9);
    debugContainer.innerHTML = `
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">
            <button class="btn btn-link text-decoration-none" type="button" data-bs-toggle="collapse" data-bs-target="#${debugId}" aria-expanded="false">
              <i class="bi bi-bug me-2"></i>
              Debug Information
              <i class="bi bi-chevron-down ms-2" style="transition: transform 0.3s ease;"></i>
            </button>
          </h5>
        </div>
        <div id="${debugId}" class="collapse">
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <div class="card debug-card">
                  <div class="card-header bg-info text-white">
                    <h6 class="mb-0">
                      <i class="bi bi-diagram-3 me-2"></i>
                      Schema API Response
                    </h6>
                    <small>${apiBase}/schema</small>
                  </div>
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <small class="text-muted">Status: <span class="schema-status badge bg-secondary">Not loaded</span></small>
                      <button class="btn btn-sm btn-outline-primary load-schema-btn">
                        <i class="bi bi-arrow-clockwise"></i> Load
                      </button>
                    </div>
                    <pre class="schema-content bg-light p-3 rounded" style="max-height: 400px; overflow-y: auto; font-size: 12px;">Click 'Load' to fetch schema data...</pre>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="card debug-card">
                  <div class="card-header bg-success text-white">
                    <h6 class="mb-0">
                      <i class="bi bi-table me-2"></i>
                      Data API Response
                    </h6>
                    <small>${apiBase}</small>
                  </div>
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <small class="text-muted">Status: <span class="data-status badge bg-secondary">Not loaded</span></small>
                      <button class="btn btn-sm btn-outline-success load-data-btn">
                        <i class="bi bi-arrow-clockwise"></i> Load
                      </button>
                    </div>
                    <div class="mb-2">
                      <small class="text-muted">Records: <span class="data-count badge bg-info">-</span></small>
                    </div>
                    <pre class="data-content bg-light p-3 rounded" style="max-height: 400px; overflow-y: auto; font-size: 12px;">Click 'Load' to fetch data...</pre>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mt-3">
              <div class="card">
                <div class="card-header bg-warning text-dark">
                  <h6 class="mb-0">
                    <i class="bi bi-info-circle me-2"></i>
                    Configuration Information
                  </h6>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-4">
                      <h6>Current Config</h6>
                      <pre class="bg-light p-3 rounded" style="font-size: 12px;">${JSON.stringify(config, null, 2)}</pre>
                    </div>
                    <div class="col-md-4">
                      <h6>API Endpoints</h6>
                      <p><code>GET ${apiBase}/schema</code></p>
                      <p><code>GET ${apiBase}</code></p>
                      <small class="text-muted">Schema returns column definitions. Data returns records array.</small>
                    </div>
                    <div class="col-md-4">
                      <h6>Display Types</h6>
                      <p><code>text</code> - Default plain text</p>
                      <p><code>label</code> - Colored badges</p>
                      <p><code>progressBar</code> - Progress bars</p>
                      <small class="text-muted">Configure via columnConfig option.</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Store debug handlers for organized setup
    const loadSchemaBtn = debugContainer.querySelector('.load-schema-btn');
    const loadDataBtn = debugContainer.querySelector('.load-data-btn');
    const collapseElement = debugContainer.querySelector(`#${debugId}`);
    
    if (loadSchemaBtn && loadDataBtn && collapseElement) {
      debugHandlers.push({
        schemaBtn: loadSchemaBtn,
        dataBtn: loadDataBtn,
        collapseEl: collapseElement,
        container: debugContainer,
        apiBase: apiBase
      });
    }
    
    return debugContainer;
  }

  // Function to load debug data
  async function loadDebugData(url, container, type) {
    console.log(`Loading debug data: ${type} from ${url}`);
    
    const statusEl = container.querySelector(`.${type}-status`);
    const contentEl = container.querySelector(`.${type}-content`);
    const countEl = container.querySelector(`.${type}-count`);
    
    console.log('Debug elements found:', {
      statusEl: !!statusEl,
      contentEl: !!contentEl,
      countEl: !!countEl
    });
    
    if (!statusEl || !contentEl) {
      console.error('Required debug elements not found for type:', type);
      return;
    }
    
    try {
      statusEl.textContent = 'Loading...';
      statusEl.className = 'badge bg-warning';
      contentEl.textContent = 'Loading...';
      if (countEl) countEl.textContent = '-';
      
      console.log('Fetching data from:', url);
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log(`${type} data loaded:`, data);
      
      statusEl.textContent = `${response.status} OK`;
      statusEl.className = 'badge bg-success';
      
      if (type === 'data' && Array.isArray(data)) {
        if (countEl) countEl.textContent = data.length;
        // Show first 3 records for preview
        const displayData = data.length > 3 ? data.slice(0, 3) : data;
        const message = data.length > 3 ? `\n\n... and ${data.length - 3} more records` : '';
        contentEl.textContent = JSON.stringify(displayData, null, 2) + message;
      } else {
        contentEl.textContent = JSON.stringify(data, null, 2);
      }
      
      console.log(`Successfully loaded ${type} debug data`);
      
    } catch (error) {
      console.error(`Error loading ${type} debug data:`, error);
      statusEl.textContent = 'Error';
      statusEl.className = 'badge bg-danger';
      contentEl.textContent = `Error: ${error.message}`;
      if (countEl) countEl.textContent = 'Error';
    }
  }

  // Function to create intelligent combo editor for cell editing
  function createComboEditor(values, tableData) {
    console.log('Creating combo editor with values:', values);
    return function(cell, onRendered, success, cancel) {
      const currentValue = cell.getValue() || '';
      console.log('Combo editor opened for field:', cell.getField(), 'current value:', currentValue, 'available values:', values);
      
      // Create a container with input and dropdown
      const container = document.createElement('div');
      container.className = 'position-relative';
      container.style.width = '100%';
      
      // Create the input field
      const input = document.createElement('input');
      input.type = 'text';
      input.className = 'form-control form-control-sm';
      input.value = currentValue;
      input.style.paddingRight = '30px'; // Space for dropdown button
      
      // Create dropdown button
      const dropdownBtn = document.createElement('button');
      dropdownBtn.type = 'button';
      dropdownBtn.className = 'btn btn-outline-secondary btn-sm';
      dropdownBtn.style.position = 'absolute';
      dropdownBtn.style.right = '1px';
      dropdownBtn.style.top = '1px';
      dropdownBtn.style.bottom = '1px';
      dropdownBtn.style.width = '28px';
      dropdownBtn.style.zIndex = '10';
      dropdownBtn.style.border = 'none';
      dropdownBtn.style.borderLeft = '1px solid #ced4da';
      dropdownBtn.innerHTML = '<i class="bi bi-chevron-down" style="font-size: 10px;"></i>';
      
      // Create dropdown menu
      const dropdown = document.createElement('div');
      dropdown.className = 'dropdown-menu show'; // Add 'show' class for Bootstrap visibility
      dropdown.style.position = 'fixed'; // Use fixed positioning to ensure it floats above everything
      dropdown.style.zIndex = '99999'; // Very high z-index to ensure it appears above everything
      dropdown.style.maxHeight = '200px';
      dropdown.style.overflowY = 'auto';
      dropdown.style.display = 'none'; // Start hidden
      dropdown.style.border = '1px solid #ced4da';
      dropdown.style.borderRadius = '4px';
      dropdown.style.backgroundColor = 'white';
      dropdown.style.boxShadow = '0 0.5rem 1rem rgba(0, 0, 0, 0.15)';
      dropdown.style.minWidth = '150px';
      
      // Add values to dropdown
      const sortedValues = values.slice().sort();
      console.log('Sorted values for dropdown:', sortedValues);
      sortedValues.forEach((value, index) => {
        console.log(`Adding dropdown item ${index}:`, value);
        const item = document.createElement('button');
        item.type = 'button';
        item.className = 'dropdown-item d-flex justify-content-between align-items-center';
        item.style.fontSize = '12px';
        item.style.padding = '6px 12px';
        item.style.border = 'none';
        item.style.background = 'transparent';
        item.style.width = '100%';
        item.style.textAlign = 'left';
        item.style.display = 'flex';
        item.style.cursor = 'pointer';
        
        const text = document.createElement('span');
        text.textContent = value;
        item.appendChild(text);
        
        // Add count badge - use passed tableData
        const fieldName = cell.getField();
        const count = tableData.filter(d => d[fieldName] === value).length;
        const badge = document.createElement('span');
        badge.className = 'badge bg-light text-dark ms-2';
        badge.style.fontSize = '10px';
        badge.textContent = count;
        item.appendChild(badge);
        
        item.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          input.value = value;
          dropdown.style.display = 'none';
          input.focus();
        });
        
        console.log('Appending item to dropdown:', item.textContent);
        dropdown.appendChild(item);
        console.log('Dropdown children count:', dropdown.children.length);
      });
      
      // Add "Clear" option
      if (currentValue) {
        const divider = document.createElement('div');
        divider.className = 'dropdown-divider';
        dropdown.appendChild(divider);
        
        const clearItem = document.createElement('button');
        clearItem.type = 'button';
        clearItem.className = 'dropdown-item text-danger';
        clearItem.style.fontSize = '12px';
        clearItem.style.border = 'none';
        clearItem.style.background = 'transparent';
        clearItem.style.width = '100%';
        clearItem.style.textAlign = 'left';
        clearItem.style.padding = '6px 12px';
        clearItem.style.cursor = 'pointer';
        clearItem.innerHTML = '<i class="bi bi-x-circle me-2"></i>Clear value';
        clearItem.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          input.value = '';
          dropdown.style.display = 'none';
          input.focus();
        });
        dropdown.appendChild(clearItem);
      }
      
      // Toggle dropdown
      dropdownBtn.addEventListener('click', (e) => {
        console.log('Dropdown button clicked');
        e.preventDefault();
        e.stopPropagation();
        const isVisible = dropdown.style.display !== 'none';
        console.log('Current dropdown visibility:', isVisible ? 'visible' : 'hidden');
        
        if (isVisible) {
          dropdown.style.display = 'none';
        } else {
          // Position the dropdown relative to the input field
          const inputRect = input.getBoundingClientRect();
          dropdown.style.top = (inputRect.bottom + 2) + 'px';
          dropdown.style.left = inputRect.left + 'px';
          dropdown.style.width = inputRect.width + 'px';
          dropdown.style.display = 'block';
          input.focus();
        }
        console.log('Setting dropdown to:', isVisible ? 'hidden' : 'visible');
      });
      
      // Hide dropdown when clicking outside
      document.addEventListener('click', function hideDropdown(e) {
        if (!container.contains(e.target) && !dropdown.contains(e.target)) {
          dropdown.style.display = 'none';
          document.removeEventListener('click', hideDropdown);
        }
      });
      
      // Cleanup function to remove dropdown from body when editor is destroyed
      const cleanup = () => {
        if (dropdown.parentNode) {
          dropdown.parentNode.removeChild(dropdown);
        }
      };
      
      // Handle escape key and blur events
      input.addEventListener('blur', (e) => {
        // Small delay to allow click events on dropdown items
        setTimeout(() => {
          if (!dropdown.contains(document.activeElement)) {
            dropdown.style.display = 'none';
          }
        }, 150);
      });
      
      // Filter dropdown based on input
      input.addEventListener('input', () => {
        const filterValue = input.value.toLowerCase();
        const items = dropdown.querySelectorAll('.dropdown-item:not(.text-danger)');
        let hasVisibleItems = false;
        
        items.forEach(item => {
          const text = item.querySelector('span').textContent.toLowerCase();
          const isVisible = text.includes(filterValue);
          item.style.display = isVisible ? 'block' : 'none';
          if (isVisible) hasVisibleItems = true;
        });
        
        // Show/hide dropdown based on filter results
        if (filterValue && hasVisibleItems) {
          dropdown.style.display = 'block';
        } else if (!filterValue) {
          dropdown.style.display = 'none';
        }
      });
      
      // Handle keyboard navigation
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          success(input.value);
        } else if (e.key === 'Escape') {
          cancel();
        } else if (e.key === 'ArrowDown' && dropdown.style.display === 'none') {
          dropdown.style.display = 'block';
          e.preventDefault();
        }
      });
      
      // Assemble the editor
      container.appendChild(input);
      container.appendChild(dropdownBtn);
      // Append dropdown to body so it can float above everything
      document.body.appendChild(dropdown);
      
      console.log('Final dropdown state:');
      console.log('- Total children:', dropdown.children.length);
      console.log('- Dropdown visible:', dropdown.style.display);
      console.log('- Dropdown positioned:', dropdown.style.position, dropdown.style.top);
      console.log('- First item text:', dropdown.children[0]?.textContent || 'No items');
      
      // Focus and select all text
      onRendered(() => {
        input.focus();
        input.select();
      });
      
      return container;
    };
  }

  // create controls + table + debug wrapped in a Bootstrap card
  container.innerHTML = '';
  const card = document.createElement('div'); card.className = 'card shadow-lg';
  
  // Add loading indicator
  const loadingDiv = document.createElement('div');
  loadingDiv.className = 'd-flex justify-content-center align-items-center p-5';
  loadingDiv.innerHTML = '<div class="spinner-border text-primary me-3" role="status"><span class="visually-hidden">Loading...</span></div><span class="text-muted">Loading patient data...</span>';
  container.appendChild(loadingDiv);
  
  const cardHeader = document.createElement('div'); cardHeader.className = 'card-header d-flex justify-content-between align-items-center';
  const controls = document.createElement('div'); controls.className = 'tc-controls d-flex gap-2 align-items-center flex-wrap';
  const dlBtn = document.createElement('button');
  dlBtn.innerHTML = '<i class="bi bi-download me-1"></i>Download CSV';
  dlBtn.type = 'button';
  dlBtn.className = 'btn btn-success btn-sm';
  dlBtn.title = 'Export table data as CSV';
  // (will append buttons later in a logical order)

  // Save button moved inside the component (was previously in the page header)
  const saveBtn = document.createElement('button');
  saveBtn.id = 'save-data-btn';
  saveBtn.type = 'button';
  saveBtn.className = 'btn btn-primary btn-sm';
  saveBtn.title = 'Save filtered and edited data to server';
  saveBtn.innerHTML = '<i class="bi bi-cloud-upload me-1"></i>Save Data';
  // Delegate to the global save function (defined later) when clicked
  saveBtn.addEventListener('click', () => { if (typeof window.saveToServer === 'function') window.saveToServer(); });

  const colSelectWrap = document.createElement('div');
  colSelectWrap.className = 'dropdown';
  const colBtn = document.createElement('button');
  colBtn.id = 'tc-col-btn';
  colBtn.className = 'btn btn-outline-secondary btn-sm dropdown-toggle';
  colBtn.setAttribute('data-bs-toggle','dropdown');
  colBtn.setAttribute('aria-expanded','false');
  colBtn.innerHTML = '<i class="bi bi-columns-gap me-1"></i>Columns';
  colBtn.title = 'Show/hide table columns';
  colSelectWrap.appendChild(colBtn);
  const colMenu = document.createElement('ul');
  colMenu.className = 'dropdown-menu dropdown-menu-end p-2';
  colSelectWrap.appendChild(colMenu);

  const tableDiv = document.createElement('div');
  tableDiv.className = 'tc-table';
  const debug = document.createElement('pre');
  debug.className = 'tc-debug';

  // Add table info section
  const tableInfo = document.createElement('div');
  tableInfo.className = 'd-flex align-items-center gap-2';
  tableInfo.innerHTML = '<i class="bi bi-info-circle text-muted"></i><small class="text-muted" id="table-info">Loading...</small>';
  
  cardHeader.appendChild(controls);
  cardHeader.appendChild(tableInfo);
  card.appendChild(cardHeader);
  
  // Top pagination container
  const topPagerContainer = document.createElement('div'); 
  topPagerContainer.className = 'border-bottom bg-light p-2';
  const topPager = document.createElement('div');
  topPager.className = 'tc-pager';
  topPagerContainer.appendChild(topPager);
  card.appendChild(topPagerContainer);
  
  const cardBody = document.createElement('div'); cardBody.className = 'card-body p-2';
  const tableWrapper = document.createElement('div'); tableWrapper.className = 'table-responsive';
  tableWrapper.appendChild(tableDiv);
  cardBody.appendChild(tableWrapper);
  card.appendChild(cardBody);
  
  const cardFooter = document.createElement('div'); cardFooter.className = 'card-footer p-2';
  // cardFooter.appendChild(debug);
  // Bottom pagination container
  const bottomPager = document.createElement('div');
  bottomPager.className = 'tc-pager';
  cardFooter.appendChild(bottomPager);
  card.appendChild(cardFooter);
  container.appendChild(card);

  // Conditionally add debug section based on configuration
  if (config.showDebug) {
    console.log('Creating debug section with config:', config);
    const debugSection = createDebugSection(apiBase);
    container.appendChild(debugSection);
    console.log('Debug section added to container');
  }

  // fetch data and schema
  let schema, data;
  try{
    console.log('🔄 Fetching data and schema from:', apiBase);
    [schema, data] = await Promise.all([
      fetch(apiBase + '/schema').then(r => { 
        console.log('Schema response status:', r.status);
        if(!r.ok) throw new Error('Schema fetch failed ' + r.status); 
        return r.json(); 
      }),
      fetch(apiBase).then(r => { 
        console.log('Data response status:', r.status);
        if(!r.ok) throw new Error('Data fetch failed ' + r.status); 
        return r.json(); 
      })
    ]);
    
    console.log('✅ Data fetched successfully:', { schema: schema?.columns?.length, data: data?.length });
    
    // Remove loading indicator
    container.removeChild(loadingDiv);
    
  } catch(err){
    // Show error with better styling
    container.innerHTML = `
      <div class="alert alert-danger d-flex align-items-center" role="alert">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        <div>
          <strong>Error loading data:</strong> ${err.toString()}
        </div>
      </div>
    `;
    console.error(err);
    return null;
  }

  // Update debug info with better formatting
  debug.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-2">
      <strong><i class="bi bi-code-slash me-1"></i>Debug Information</strong>
      <small class="text-muted">${data.length} records loaded</small>
    </div>
    <div class="row">
      <div class="col-md-6">
        <strong>Schema (${schema.columns.length} columns):</strong>
        <pre class="mt-1">${JSON.stringify(schema.columns.slice(0,5), null, 2)}</pre>
      </div>
      <div class="col-md-6">
        <strong>Data Sample:</strong>
        <pre class="mt-1">${JSON.stringify(data.slice(0,2), null, 2)}</pre>
      </div>
    </div>
  `;
  
  // Update table info
  const tableInfoEl = document.getElementById('table-info');
  if(tableInfoEl) {
    tableInfoEl.innerHTML = `${data.length} records, ${schema.columns.length} columns • Paginated`;
  }

  // helper: debounce
  function debounce(fn, wait){
    let t;
    return function(...args){ clearTimeout(t); t = setTimeout(() => fn.apply(this,args), wait); };
  }

  // storage key for filters
  const storageKey = 'tc_filters_' + config.storageKey;

  // persist header filter UI state to avoid accidental clearing when Tabulator
  // re-renders header filter elements. Keyed by field name.
  const headerFilterState = {};

     // build Tabulator columns from schema with smart header filters
   const columns = schema.columns.map(col => {
     const field = col.field;
     const title = col.label || field;
  const isNumber = (col.sorter === 'number');
  // client-provided column config (if any)
  const clientFieldConfig = (config.columnConfig && config.columnConfig[field]) ? config.columnConfig[field] : {};
  // Merge schema column config and client config - client options override schema on conflict
  const mergedFieldConfig = Object.assign({}, col, clientFieldConfig);
  // Use the merged config to determine displayType (client wins when same parameter exists)
  const displayType = mergedFieldConfig.displayType || null;

     // compute unique values for this column from the data (used for select and editing)
     const values = Array.from(new Set(data.map(d => d[field]).filter(v => v !== null && v !== undefined && v !== '')));
     
     // Debug problematic columns
     if (field === 'smoking_status' || field === 'smoking') {
       console.log(`DETAILED DEBUG for ${field}:`);
       console.log('Raw values from first 5 records:', data.slice(0, 5).map(d => d[field]));
       console.log('All unique values:', values);
       console.log('Value types:', values.map(v => typeof v));
     } else {
       console.log(`Column ${field}: ${values.length} unique values:`, values);
     }

           const colDef = {
        title: title,
        field: field,
        visible: !col.hidden,
        sorter: col.sorter || undefined,
        editable: col.editable || false, // Keep the editable property from schema
      };
      
      // Store the original editor separately in our mapping
      if (col.editable) {
        originalEditors[field] = values.length > 0 && values.length <= 6 ? 
          (console.log(`Using combo editor for ${field} with values:`, values), createComboEditor(values, data)) : 
          (console.log(`Using input editor for ${field} (${values.length} values)`), 'input');
        
        // Create a conditional editor that only works when editing is enabled
        colDef.editor = function(cell, onRendered, success, cancel) {
          if (!editingEnabled) {
            console.log('❌ EDITING BLOCKED: edit mode is OFF');
            cancel();
            return false;
          }
          
          const originalEditor = originalEditors[field];
          if (originalEditor && typeof originalEditor === 'function') {
            return originalEditor(cell, onRendered, success, cancel);
          } else if (originalEditor === 'input') {
            // Simple input editor
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'form-control form-control-sm';
            input.value = cell.getValue() || '';
            
            input.addEventListener('blur', () => success(input.value));
            input.addEventListener('keydown', (e) => {
              if (e.key === 'Enter') success(input.value);
              if (e.key === 'Escape') cancel();
            });
            
            onRendered(() => {
              input.focus();
              input.select();
            });
            
            return input;
          }
          
          cancel();
          return false;
        };
      }
     
     // Log column creation details for debugging
     console.log(`📋 Column created: ${field}`);
     console.log(`  - Schema editable: ${col.editable}`);
     console.log(`  - Final editable: ${colDef.editable}`);
     console.log(`  - Has editor: ${!!colDef.editor}`);
     console.log(`  - Editor type: ${colDef.editor}`);

    // choose header filter strategy
    // if very few distinct values, show select (less than 6)
    if (values.length > 0 && values.length < 6) {
      // use the new 'list' header filter and provide values to avoid Tabulator warnings
      colDef.headerFilter = 'list';
      const vals = values.slice().sort().map(v => String(v));
      colDef.headerFilterParams = { values: vals };
      colDef.headerFilterFunc = '=';
      colDef.headerFilterLiveFilter = true;
    } else if (isNumber) {
      // numeric -> custom operator + input filter
  colDef.headerFilter = function(cell, onRendered, success, cancel) {
    const container = document.createElement('div');
    container.style.display = 'flex';
    container.style.flexDirection = 'row';
    container.style.gap = '6px';
    container.style.alignItems = 'center';
    container.style.flexWrap = 'nowrap';
    const sel = document.createElement('select');
    sel.className = 'form-select form-select-sm';
    sel.style.display = 'inline-block';
    sel.style.width = '60px';
    sel.style.padding = '0 .25rem';
    ['','>','<','=', '>=', '<='].forEach(op => { const o = document.createElement('option'); o.value = op; o.text = op || 'Op'; sel.appendChild(o); });
    const inp = document.createElement('input');
    inp.type = 'number'; inp.className = 'form-control form-control-sm';
    inp.style.display = 'inline-block'; inp.style.width = '80px'; inp.style.boxSizing = 'border-box';
  const saveAndSuccess = debounce(() => {
    const hv = (sel.value||'') + (inp.value||'');
    // store in local state so we can restore if Tabulator re-renders the header
    if (hv && String(hv).trim() !== '') headerFilterState[field] = hv; else delete headerFilterState[field];

    // Prefer to set the filter through Tabulator API when available to avoid
    // the header element being re-created while typing (which can drop focus
    // and clear the input). If table isn't ready, fall back to success().
    try {
      if (typeof table !== 'undefined' && table.setHeaderFilterValue) {
        table.setHeaderFilterValue(field, hv);
        return;
      }
    } catch (e) {
      // ignore and fallback to success
    }

    try { success(hv); } catch (e) { /* ignore */ }
  }, 300);
  sel.addEventListener('change', saveAndSuccess);
  inp.addEventListener('input', saveAndSuccess);
    container.appendChild(sel); container.appendChild(inp);
    onRendered(() => {
      // Initialize filter UI from our stored headerFilterState. We avoid
      // calling Tabulator's getHeaderFilterValue here because it may warn if
      // the table is not yet fully initialized. The stored state is updated
      // whenever the user changes the operator/value.
      try {
        const current = headerFilterState[field];
        if (current) {
          const m = String(current).match(/^(>=|<=|>|<|=)?(.*)$/);
          if (m) {
            sel.value = m[1] || '=';
            inp.value = m[2] || '';
          }
        }
      } catch (e) {
        // ignore
      }
      // focus the input for quick typing
      try { inp.focus(); } catch(e){}
    });
    return container;
  };
  colDef.headerFilterFunc = function(headerValue, rowValue) {
        try {
          if(!headerValue) return true;
          const m = headerValue.match(/^(>=|<=|>|<|=)?(.*)$/);
          if(!m) return true;
          const op = m[1] || '=';
          const sval = m[2];
          if(sval === '') return true;
          const num = parseFloat(sval);
          const rv = Number(rowValue);
          if(isNaN(num) || isNaN(rv)) return false;
          switch(op){
            case '>': return rv > num;
            case '<': return rv < num;
            case '>=': return rv >= num;
            case '<=': return rv <= num;
            case '=': return rv === num;
            default: return rv === num;
          }
        } catch(e){ return true; }
      };
    } else {
      // default text filter -> contains with debounce
      colDef.headerFilterFunc = 'like';
      colDef.headerFilterLiveFilter = true;
      // wrap headerFilterElement to debounce
      colDef.headerFilter = function(cell, onRendered, success, cancel){
        const el = document.createElement('input');
        el.type = 'text'; el.className = 'form-control form-control-sm';
        el.addEventListener('input', debounce(() => { 
          console.log(`Filter applied to ${field}:`, el.value);
          success(el.value); 
        }, 300));
        onRendered(() => {});
        return el;
      };
    }

    // Apply custom formatters using the merged field config (client overrides schema)
    if (displayType === 'label') {
      // pass a mapping with the merged config so the formatter finds it via columnConfig[fieldName]
      colDef.formatter = createLabelFormatter(field, { [field]: mergedFieldConfig }, values);
    } else if (displayType === 'progressBar' && isNumber) {
      // Determine min/max: prefer schema-provided min/max, otherwise derive from data
      const minValue = (typeof col.min === 'number') ? col.min : (() => {
        const numericValues = data.map(d => parseFloat(d[field])).filter(v => !isNaN(v));
        return numericValues.length ? Math.min(...numericValues) : 0;
      })();
      const maxValue = (typeof col.max === 'number') ? col.max : (() => {
        const numericValues = data.map(d => parseFloat(d[field])).filter(v => !isNaN(v));
        return numericValues.length ? Math.max(...numericValues) : (minValue + 100);
      })();

  // Pass the merged field config (client options override schema)
  colDef.formatter = createProgressBarFormatter(field, mergedFieldConfig, minValue, maxValue);
    } else if(col.hyperlink){
      colDef.formatter = function(cell){
        const v = cell.getValue();
        if(v===null||v===undefined) return '';
        const url = col.hyperlink.replace('{value}', encodeURIComponent(v));
        return `<a href='${url}' target='_blank' rel='noopener'>${v}</a>`;
      };
    }

    return colDef;
  });

  // add a left-most actions column with selection and delete buttons
  columns.unshift({
         formatter: function(cell, formatterParams, onRendered){
       const row = cell.getRow();
       const rowIndex = row.getIndex();
       
       // Row selection icon and delete icon
       const html = "<div style='display: flex; gap: 1px; justify-content: center;'>" +
         "<button class='btn btn-sm btn-outline-primary tc-row-select' data-row-index='" + rowIndex + "' title='Select Row' aria-label='Select Row' style='padding: 1px 3px;'>" +
           "<i class='bi bi-square' aria-hidden='true' style='font-size: 9px;'></i>" +
         "</button>" +
         "<button class='btn btn-sm btn-outline-danger tc-row-del' data-row-index='" + rowIndex + "' title='Delete Record' aria-label='Delete' style='padding: 2px 4px;'>" +
           "<i class='bi bi-x' aria-hidden='true' style='font-size: 10px;'></i>" +
         "</button>" +
       "</div>";
       
       // Add event listeners after rendering
       onRendered(() => {
         const container = cell.getElement();
         const selectBtn = container.querySelector('.tc-row-select');
         const deleteBtn = container.querySelector('.tc-row-del');
         
         if (selectBtn) {
           selectBtn.addEventListener('click', (e) => {
             e.stopPropagation();
             const rowElement = row.getElement();
             const icon = selectBtn.querySelector('i');
             
             if(rowElement.classList.contains('tabulator-selected')) {
               // Deselect row
               rowElement.classList.remove('tabulator-selected');
               selectBtn.classList.remove('selected');
               icon.className = 'bi bi-square';
             } else {
               // Select row
               rowElement.classList.add('tabulator-selected');
               selectBtn.classList.add('selected');
               icon.className = 'bi bi-check-square-fill';
             }
           });
         }
         
         if (deleteBtn) {
           deleteBtn.addEventListener('click', (e) => {
             e.stopPropagation();
             if(window.confirm('⚠️ Are you sure you want to delete this record?\n\nThis action cannot be undone.')) {
               // Add fade out animation before deletion
               const rowElement = row.getElement();
               rowElement.style.transition = 'all 0.3s ease';
               rowElement.style.opacity = '0.5';
               rowElement.style.transform = 'translateX(-20px)';
               
               setTimeout(() => {
                 row.delete();
               }, 300);
             }
           });
         }
       });
       
       return html;
     },
    title: '<i class="bi bi-gear-fill"></i>',
    width: 70,
    hozAlign: 'center',
    headerSort: false,
         // NO cellClick handler - removed as requested
  });

  // create Tabulator
  // ensure Tabulator fills the card body width
  tableDiv.style.width = '100%';
  tableDiv.style.minHeight = options.minHeight || '300px';
  
  console.log('🔄 Creating Tabulator table with:', { columns: columns.length, data: data.length });
  
           const table = new Tabulator(tableDiv, {
      data: data,
      columns: columns,
      layout: options.layout || 'fitDataFill',
      pagination: 'local',
      paginationSize: config.pageSize,
      paginationSizeSelector: [10, 25, 50, 100],
      paginationElement: bottomPager,
      paginationCounter: 'rows',
      paginationCounterElement: function(count, max) {
        return `<i class="bi bi-table me-1"></i>Showing ${count} of ${max} records`;
      },
  movableColumns: true,
  // Disable Tabulator's built-in resizing so we can control where resize
  // handles are active (headers for columns, first column for rows).
  resizableColumns: false,
  resizableRows: false,
      selectable: false, // Disable automatic row selection - only allow through button
      selectableRangeMode: "click",
      // No editing through Tabulator - removed as requested
      validationMode: "blocking",
    initialSort: schema.columns.filter(c => c.sort).map(c => ({column: c.field, dir: c.sort})),
         
    cellEdited: function(cell){
      // placeholder for persistence
      console.log('Cell edited:', cell.getField(), 'new value:', cell.getValue());
    },
    dataLoaded: function(data) {
      console.log("⚠️ Table data loaded/reloaded:", data.length, "records - this might clear filters!");
    },
    dataChanged: function(data) {
      console.log("⚠️ Table data changed:", data.length, "records - this might clear filters!");
    },
    tableBuilt: function(){
      console.log("✅ Table built successfully");
      // Initialize pagination cloning after table is fully built
      setTimeout(() => {
        initializeDualPagination();
      }, 200);
  // Add custom header column resizers and row resizers (first column)
  try { addHeaderResizers(); addFirstColumnRowResizers(); } catch(e){ console.warn('addHeaderResizers error', e); }
      // Restore any stored header filter values now that the table is built.
      try {
        Object.entries(headerFilterState).forEach(([f, v]) => {
          try { table.setHeaderFilterValue(f, v); } catch (e) { /* ignore per-field errors */ }
        });
      } catch (e) { console.warn('Failed to restore header filters after build', e); }
    },
    paginationInitialized: function(){
      console.log("✅ Pagination initialized");
      // Also try when pagination is specifically initialized
      setTimeout(() => {
        initializeDualPagination();
      }, 100);
    }
  });

  // Function to initialize dual pagination
  function initializeDualPagination() {
    // Check for any pagination content in bottom pager
    const hasBottomContent = bottomPager.children.length > 0;
    const bottomPagination = bottomPager.querySelector('.tabulator-paginator') || bottomPager.firstElementChild;
    
    console.log('Checking pagination initialization:', {
      hasBottomContent: hasBottomContent,
      bottomPagination: !!bottomPagination,
      topPagerChildren: topPager.children.length,
      bottomPagerHTML: bottomPager.innerHTML.substring(0, 150),
      bottomPagerChildren: bottomPager.children.length
    });
    
    if(hasBottomContent && topPager.children.length === 0) {
      console.log('✅ Initializing dual pagination...');
      
      // Clone all bottom pagination content to the top
      Array.from(bottomPager.children).forEach(child => {
        const clonedChild = child.cloneNode(true);
        topPager.appendChild(clonedChild);
      });
      
      // Style both pagination controls
      [bottomPager, topPager].forEach(pagerEl => {
        const paginationControls = pagerEl.querySelector('.tabulator-page-size');
        if(paginationControls) {
          const label = paginationControls.parentNode.querySelector('label');
          if(label) {
            label.innerHTML = '<i class="bi bi-list-ul me-1"></i>Rows per page:';
          }
        }
      });
      
      // Sync events between top and bottom pagination
      syncPaginationControls(topPager, bottomPager, table);
      
      console.log('✅ Dual pagination initialized successfully');
      console.log('Top pager HTML:', topPager.innerHTML.substring(0, 150));
    } else if(!hasBottomContent) {
      console.log('⚠️ Bottom pagination content not found yet');
    } else {
      console.log('ℹ️ Top pagination already exists');
    }
  }

  // Add header-only column resizers (attach small handles at the right edge of each header cell)
  function addHeaderResizers() {
    try {
      const headers = card.querySelectorAll('.tabulator-col');
      headers.forEach(h => {
        // Avoid adding multiple handles
        if (h.querySelector('.tc-header-resizer')) return;
        const handle = document.createElement('div');
        handle.className = 'tc-header-resizer';
        handle.style.position = 'absolute';
        handle.style.right = '0';
        handle.style.top = '0';
        handle.style.width = '6px';
        handle.style.height = '100%';
        handle.style.cursor = 'col-resize';
        handle.style.zIndex = '10';
        handle.style.userSelect = 'none';
        handle.style.background = 'transparent';
        h.style.position = 'relative';
        h.appendChild(handle);

        let startX, startWidth, colEl;
        const onMouseDown = (e) => {
          e.preventDefault();
          startX = e.clientX;
          colEl = h;
          const w = colEl.getBoundingClientRect().width;
          startWidth = w;
          document.addEventListener('mousemove', onMouseMove);
          document.addEventListener('mouseup', onMouseUp, { once: true });
        };
        const onMouseMove = (e) => {
          if(!colEl) return;
          const dx = e.clientX - startX;
          const newW = Math.max(30, startWidth + dx);
          // Apply directly to the column header and matching cells
          try {
            const field = colEl.getAttribute('tabulator-field');
            if(field) table.getColumn(field).getElement().style.width = newW + 'px';
            colEl.style.width = newW + 'px';
          } catch(e) {
            colEl.style.width = newW + 'px';
          }
        };
        const onMouseUp = (e) => {
          document.removeEventListener('mousemove', onMouseMove);
          colEl = null;
        };

        handle.addEventListener('mousedown', onMouseDown);
      });
    } catch (e) { console.warn('addHeaderResizers failed', e); }
  }

  // Watch for table DOM changes and re-apply resizer handles when necessary
  try {
    const mo = new MutationObserver(() => {
      try { addHeaderResizers(); addFirstColumnRowResizers(); } catch(e){}
    });
    mo.observe(card, { childList: true, subtree: true });
  } catch(e) { /* ignore */ }

  // Add row height resizers only in the first column cells (actions column)
  function addFirstColumnRowResizers() {
    try {
      const rows = card.querySelectorAll('.tabulator-row');
      rows.forEach(r => {
        // find first cell
        const firstCell = r.querySelector('.tabulator-cell');
        if(!firstCell) return;
        if (firstCell.querySelector('.tc-row-resizer')) return;
        const handle = document.createElement('div');
        handle.className = 'tc-row-resizer';
        handle.style.position = 'absolute';
        handle.style.bottom = '0';
        handle.style.left = '0';
        handle.style.right = '0';
        handle.style.height = '6px';
        handle.style.cursor = 'row-resize';
        handle.style.zIndex = '10';
        handle.style.userSelect = 'none';
        handle.style.background = 'transparent';
        firstCell.style.position = 'relative';
        firstCell.appendChild(handle);

        let startY, startH, rowEl;
        const onMouseDown = (e) => {
          e.preventDefault();
          startY = e.clientY;
          rowEl = r;
          startH = rowEl.getBoundingClientRect().height;
          document.addEventListener('mousemove', onMouseMove);
          document.addEventListener('mouseup', onMouseUp, { once: true });
        };
        const onMouseMove = (e) => {
          if(!rowEl) return;
          const dy = e.clientY - startY;
          const newH = Math.max(24, startH + dy);
          rowEl.style.height = newH + 'px';
          // apply to all cells in the row
          Array.from(rowEl.querySelectorAll('.tabulator-cell')).forEach(c => c.style.height = newH + 'px');
        };
        const onMouseUp = (e) => {
          document.removeEventListener('mousemove', onMouseMove);
          rowEl = null;
        };

        handle.addEventListener('mousedown', onMouseDown);
      });
    } catch (e) { console.warn('addFirstColumnRowResizers failed', e); }
  }

  // Function to sync pagination controls between top and bottom
  function syncPaginationControls(topPager, bottomPager, table) {
    console.log('Setting up pagination sync...');
    
    // Store pagination handlers for organized setup
    paginationHandlers.push({
      topPager: topPager,
      bottomPager: bottomPager,
      table: table
    });
    
    // Setup pagination sync events after handlers are stored
    setupPaginationEvents();
  }

  // Add column menu header
  const menuHeader = document.createElement('li');
  menuHeader.innerHTML = '<h6 class="dropdown-header"><i class="bi bi-eye-fill me-1"></i>Toggle Columns</h6>';
  colMenu.appendChild(menuHeader);
  
  const divider = document.createElement('li');
  divider.innerHTML = '<hr class="dropdown-divider">';
  colMenu.appendChild(divider);
  
  // populate column menu using bootstrap dropdown items
  columns.forEach(col => {
    // skip generated columns that don't have a field (like the delete button column)
    if(!col.field) return;
    const li = document.createElement('li');
    li.className = 'dropdown-item d-flex align-items-center';
    li.style.cursor = 'pointer';
    
    const cb = document.createElement('input'); 
    cb.type='checkbox'; 
    cb.checked = col.visible !== false; 
    cb.className='form-check-input me-2';
    cb.id = `col-toggle-${col.field}`;
    
    const label = document.createElement('label'); 
    label.className='form-check-label flex-grow-1'; 
    label.setAttribute('for', cb.id);
    label.innerHTML = `<i class="bi bi-columns me-1"></i>${col.title}`;
    
    const toggleColumn = () => {
      table.toggleColumn(col.field);
      // Add visual feedback
      if(cb.checked) {
        li.style.background = 'rgba(40, 167, 69, 0.1)';
      } else {
        li.style.background = 'rgba(220, 53, 69, 0.1)';
      }
      setTimeout(() => {
        li.style.background = '';
      }, 500);
    };
    
    // Store these for later organized event setup
    columnToggleHandlers.push({ checkbox: cb, listItem: li, toggleFn: toggleColumn });
    
    li.appendChild(cb); 
    li.appendChild(label);
    colMenu.appendChild(li);
  });
  
  // Add select all/none options
  const divider2 = document.createElement('li');
  divider2.innerHTML = '<hr class="dropdown-divider">';
  colMenu.appendChild(divider2);
  
  const selectAllLi = document.createElement('li');
  selectAllLi.className = 'dropdown-item d-flex gap-2';
  const selectAllBtn = document.createElement('button');
  selectAllBtn.className = 'btn btn-outline-success btn-sm flex-fill';
  selectAllBtn.innerHTML = '<i class="bi bi-check-all me-1"></i>Show All';
  
  const selectNoneBtn = document.createElement('button');
  selectNoneBtn.className = 'btn btn-outline-danger btn-sm flex-fill';
  selectNoneBtn.innerHTML = '<i class="bi bi-x-lg me-1"></i>Hide All';
  
  // Store for organized event setup
  const showAllColumnsBtn = selectAllBtn;
  const hideAllColumnsBtn = selectNoneBtn;
  
  selectAllLi.appendChild(selectAllBtn);
  selectAllLi.appendChild(selectNoneBtn);
  colMenu.appendChild(selectAllLi);

  // Add refresh button
  const refreshBtn = document.createElement('button');
  refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise me-1"></i>Refresh';
  refreshBtn.type = 'button';
  refreshBtn.className = 'btn btn-outline-info btn-sm';
  refreshBtn.title = 'Refresh table data';
  
  // Add clear filters button
  const clearFiltersBtn = document.createElement('button');
  clearFiltersBtn.innerHTML = '<i class="bi bi-filter-circle-fill me-1"></i>Clear Filters';
  clearFiltersBtn.type = 'button';
  clearFiltersBtn.className = 'btn btn-outline-warning btn-sm';
  clearFiltersBtn.title = 'Clear all column filters';
  
  // Add edit toggle button
  const editToggleBtn = document.createElement('button');
  editToggleBtn.innerHTML = '<i class="bi bi-pencil-square me-1"></i>Enable Edit';
  editToggleBtn.type = 'button';
  editToggleBtn.className = 'btn btn-outline-primary btn-sm';
  editToggleBtn.title = 'Toggle table editing mode';
  // Now that the main control buttons are created, append them to the controls in logical order
  // Order: Refresh, Clear Filters, Edit Toggle, Save, Download, Columns
  controls.appendChild(refreshBtn);
  controls.appendChild(clearFiltersBtn);
  controls.appendChild(editToggleBtn);
  controls.appendChild(saveBtn);
  controls.appendChild(dlBtn);
  controls.appendChild(colSelectWrap);
  
  // === 2. COLUMN TOGGLE EVENTS ===
  function setupColumnToggleEvents() {
    // Individual column toggles
    columnToggleHandlers.forEach(handler => {
      handler.checkbox.onchange = handler.toggleFn;
      handler.listItem.onclick = (e) => { 
        if(e.target === handler.checkbox) return; // Don't double-toggle
        handler.checkbox.checked = !handler.checkbox.checked; 
        handler.toggleFn(); 
      };
    });
    
    // Show all columns button
    showAllColumnsBtn.onclick = () => {
      columns.forEach(col => {
        if(col.field) {
          table.showColumn(col.field);
          const cb = document.getElementById(`col-toggle-${col.field}`);
          if(cb) cb.checked = true;
        }
      });
    };
    
    // Hide all columns button
    hideAllColumnsBtn.onclick = () => {
      columns.forEach(col => {
        if(col.field) {
          table.hideColumn(col.field);
          const cb = document.getElementById(`col-toggle-${col.field}`);
          if(cb) cb.checked = false;
        }
      });
    };
  }
  
  // === 3. CONTROL BUTTON EVENTS ===
  function setupControlButtonEvents() {
    // Download CSV button
    dlBtn.addEventListener('click', () => {
      const originalContent = dlBtn.innerHTML;
      dlBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Downloaded!';
      dlBtn.className = 'btn btn-success btn-sm';
      
      table.download('csv', config.filename + '.csv');
      
      setTimeout(() => {
        dlBtn.innerHTML = originalContent;
        dlBtn.className = 'btn btn-success btn-sm';
      }, 2000);
    });
    
    // Refresh data button
    refreshBtn.addEventListener('click', async () => {
      const originalContent = refreshBtn.innerHTML;
      refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise me-1 spin"></i>Refreshing...';
      refreshBtn.disabled = true;
      
      try {
        const newData = await fetch(apiBase).then(r=>r.json());
        table.setData(newData);
        
        // Update table info
        const tableInfoEl = document.getElementById('table-info');
        if(tableInfoEl) {
          tableInfoEl.innerHTML = `${newData.length} records, ${schema.columns.length} columns • Paginated`;
        }
        
        refreshBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Refreshed!';
        setTimeout(() => {
          refreshBtn.innerHTML = originalContent;
          refreshBtn.disabled = false;
        }, 1500);
      } catch(err) {
        refreshBtn.innerHTML = '<i class="bi bi-x-circle me-1"></i>Error';
        setTimeout(() => {
          refreshBtn.innerHTML = originalContent;
          refreshBtn.disabled = false;
        }, 2000);
      }
    });
    
         // Clear filters button
     clearFiltersBtn.addEventListener('click', () => {
       const originalContent = clearFiltersBtn.innerHTML;
       clearFiltersBtn.innerHTML = '<i class="bi bi-arrow-clockwise me-1 spin"></i>Clearing...';
       clearFiltersBtn.disabled = true;
       
       // Clear all header filters
       table.clearHeaderFilter();
       
       // Clear from localStorage
       localStorage.removeItem(storageKey);
       
       // Show success feedback
       clearFiltersBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Cleared!';
       setTimeout(() => {
         clearFiltersBtn.innerHTML = originalContent;
         clearFiltersBtn.disabled = false;
       }, 1500);
     });
     
                                   // Edit toggle button - SIMPLE FLAG-BASED APPROACH
       editToggleBtn.addEventListener('click', () => {
         // Prevent multiple rapid clicks
         if (editToggleBtn.disabled) return;
         editToggleBtn.disabled = true;
         
         try {
           editingEnabled = !editingEnabled;
           
           if (editingEnabled) {
             // Enable editing - full color button
             editToggleBtn.className = 'btn btn-primary btn-sm';
             editToggleBtn.innerHTML = '<i class="bi bi-pencil-square me-1"></i>Disable Edit';
             editToggleBtn.title = 'Click to disable table editing';
             
             // Add visual indicator to table container
             const tableContainer = tableDiv.closest('.card');
             if (tableContainer) {
               tableContainer.classList.add('editing-mode');
             }
             
             // Update table info to show editing status
             const tableInfoEl = document.getElementById('table-info');
             if (tableInfoEl) {
               tableInfoEl.innerHTML = `<span class="badge bg-success me-2">✏️ EDITING ENABLED</span>${data.length} records, ${schema.columns.length} columns • Double-click cells to edit`;
             }
             
             // Show success feedback immediately
             showNotification('Table editing enabled - Double-click cells to edit', 'success');
             
           } else {
             // Disable editing - outline button
             editToggleBtn.className = 'btn btn-outline-primary btn-sm';
             editToggleBtn.innerHTML = '<i class="bi bi-pencil-square me-1"></i>Enable Edit';
             editToggleBtn.title = 'Click to enable table editing';
             
             // Remove visual indicator from table container
             const tableContainer = tableDiv.closest('.card');
             if (tableContainer) {
               tableContainer.classList.remove('editing-mode');
             }
             
             // Update table info to show normal status
             const tableInfoEl = document.getElementById('table-info');
             if (tableInfoEl) {
               tableInfoEl.innerHTML = `${data.length} records, ${schema.columns.length} columns • Paginated`;
             }
             
             // Show success feedback immediately
             showNotification('Table editing disabled', 'info');
           }
         } catch (error) {
           console.error('Error toggling edit mode:', error);
           // Revert state on error
           editingEnabled = !editingEnabled;
           showNotification('Error toggling edit mode: ' + error.message, 'error');
         } finally {
           // Re-enable button immediately
           editToggleBtn.disabled = false;
         }
       });
  }
  
  // === 4. PAGINATION EVENTS ===
  function setupPaginationEvents() {
    paginationHandlers.forEach(handler => {
      const { topPager, bottomPager, table } = handler;
      
      // Page size selector sync
      topPager.addEventListener('change', function(e) {
        if(e.target.classList.contains('tabulator-page-size')) {
          console.log('Top size selector changed:', e.target.value);
          const bottomSelect = bottomPager.querySelector('select.tabulator-page-size');
          if(bottomSelect) {
            bottomSelect.value = e.target.value;
            table.setPageSize(parseInt(e.target.value));
          }
        }
      });
      
      // Page navigation sync
      topPager.addEventListener('click', function(e) {
        if(e.target.classList.contains('tabulator-page')) {
          e.preventDefault();
          e.stopPropagation();
          console.log('Top page button clicked');
          
          // Find corresponding bottom button
          const topButtons = topPager.querySelectorAll('.tabulator-page');
          const bottomButtons = bottomPager.querySelectorAll('.tabulator-page');
          
          const index = Array.from(topButtons).indexOf(e.target);
          if(index >= 0 && bottomButtons[index]) {
            bottomButtons[index].click();
          }
        }
      });
      
      // Mutation observer for bottom pagination sync
      let isUpdating = false;
      const observer = new MutationObserver(function(mutations) {
        if(isUpdating) return;
        
        mutations.forEach(function(mutation) {
          if(mutation.type === 'childList' || mutation.type === 'attributes') {
            isUpdating = true;
            setTimeout(() => {
              const bottomSelect = bottomPager.querySelector('select.tabulator-page-size');
              const topSelect = topPager.querySelector('select.tabulator-page-size');

              // Sync page size select values if different
              if (bottomSelect && topSelect && bottomSelect.value !== topSelect.value) {
                topSelect.value = bottomSelect.value;
              }

              // Keep the top pager markup in sync with the bottom pager so
              // active page highlighting and disabled prev/next states are mirrored.
              try {
                const bottomHTML = bottomPager.innerHTML;
                if (topPager.innerHTML !== bottomHTML) {
                  // Replace top pager content with the bottom pager content snapshot.
                  // Event delegation on topPager remains attached and will continue to work.
                  topPager.innerHTML = bottomHTML;
                }
              } catch (e) {
                console.warn('Failed to sync top pager HTML:', e);
              }

              isUpdating = false;
            }, 10);
          }
        });
      });
      
      observer.observe(bottomPager, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'aria-label']
      });
    });
  }
  
  // === 5. DEBUG SECTION EVENTS ===
  function setupDebugEvents() {
    debugHandlers.forEach(handler => {
      const { schemaBtn, dataBtn, collapseEl, container, apiBase } = handler;
      
      // Schema load button
      schemaBtn.addEventListener('click', () => {
        console.log('Loading schema debug data from:', apiBase + '/schema');
        loadDebugData(apiBase + '/schema', container, 'schema');
      });
      
      // Data load button
      dataBtn.addEventListener('click', () => {
        console.log('Loading data debug data from:', apiBase);
        loadDebugData(apiBase, container, 'data');
      });
      
      // Auto-load when section expands
      collapseEl.addEventListener('shown.bs.collapse', function () {
        console.log('Debug section expanded, auto-loading data...');
        setTimeout(() => {
          schemaBtn.click();
          dataBtn.click();
        }, 300);
      });
    });
  }

  // load saved filters and apply - DISABLED per user request
  function loadFilters(){
    // Disabled: Don't recall the last user filterset from local storage
    console.log('Filter loading disabled - starting with clean filters');
    return;
    
    // Original code commented out:
    // try{
    //   const raw = localStorage.getItem(storageKey);
    //   if(!raw) return;
    //   const obj = JSON.parse(raw);
    //   Object.entries(obj).forEach(([k,v]) => {
    //     try{
    //       // only apply if the column exists in the current table
    //       if(!table.getColumn || !table.getColumn(k)){
    //         console.debug('loadFilters: skipping unknown column', k);
    //         return;
    //       }
    //       table.setHeaderFilterValue(k, v);
    //     }catch(e){ console.warn('loadFilters: failed to set filter for', k, e); }
    //   });
    // }catch(e){ console.warn('loadFilters', e); }
  }

  function saveFilters(){
    // Disabled: Don't save filters to local storage per user request
    console.log('Filter saving disabled');
    return;
    
    // Original code commented out:
    // try{
    //   const vals = {};
    // columns.forEach(c => { if(!c.field) return; const v = table.getHeaderFilterValue(c.field); if(v !== undefined && v !== null && v !== '') vals[c.field]=v; });
    //   localStorage.setItem(storageKey, JSON.stringify(vals));
    // }catch(e){ console.warn('saveFilters', e); }
  }

  // apply saved filters after Tabulator has fully built the table to avoid
  // calling setHeaderFilterValue too early which causes inconsistent behavior
  // DISABLED: Don't load filters per user request
  // table.on && table.on('tableBuilt', loadFilters);

  // Final fallback to ensure dual pagination is initialized
  setTimeout(() => {
    console.log('Final fallback pagination check...');
    initializeDualPagination();
    // Also ensure event handlers are initialized
    if (typeof initializeAllEventHandlers === 'function') {
      initializeAllEventHandlers();
    }
  }, 1500);
  
  // ===========================
  // INITIALIZE ALL EVENT HANDLERS
  // ===========================
  
  function initializeAllEventHandlers() {
    console.log('🎯 Setting up all event handlers in organized order...');
    
    // 1. Core table functionality
    setupCoreTableEvents();
    
    // 2. Column visibility controls
    setupColumnToggleEvents();
    
    // 3. Control buttons (download, refresh, clear)
    setupControlButtonEvents();
    
    // 4. Debug section (if enabled)
    if (config.showDebug && debugHandlers.length > 0) {
      setupDebugEvents();
    }
    
    // Note: Pagination events are setup automatically when pagination is initialized
    
    console.log('✅ All event handlers setup complete!');
  }
  
     // === 1. CORE TABLE EVENTS ===
   function setupCoreTableEvents() {
     // Cell editing tracking
     table.on('cellEdited', function(cell) {
       hasChanges = true;
       const change = {
         field: cell.getField(),
         oldValue: cell.getOldValue(),
         newValue: cell.getValue(),
         rowId: cell.getRow().getIndex(),
         timestamp: new Date().toISOString()
       };
       changeLog.push(change);
       console.log('Cell edited:', change);
       
       // Update save button state
       const saveBtn = document.querySelector('#save-data-btn');
       if (saveBtn && hasChanges) {
         saveBtn.classList.remove('btn-primary');
         saveBtn.classList.add('btn-warning');
         saveBtn.innerHTML = '<i class="bi bi-cloud-upload"></i> Save Changes';
       }
     });
     
                       // Double-click handler for cell editing - ONLY when editing is enabled
      table.on('cellDblClick', function(e, cell) {
        const field = cell.getField();
        console.log('🔍 DOUBLE-CLICK CAUGHT on column:', field);
        
        // Check if editing is enabled
        if (!editingEnabled) {
          console.log('❌ EDITING BLOCKED: edit mode is OFF');
          return false;
        }
        
        // Check if this column can be edited (has an original editor)
        if (originalEditors[field]) {
          console.log('✅ EDITING ALLOWED: Starting edit for column:', field);
          cell.edit();
          return true;
        } else {
          console.log('❌ EDITING BLOCKED: Column has no editor:', field);
          return false;
        }
      });
    
    // Data change notifications
    table.on('dataLoaded', function(data) {
      console.log("Table data loaded:", data.length, "records");
    });
    
    table.on('dataChanged', function(data) {
      console.log("Table data changed:", data.length, "records");
    });
    
    // Pagination initialization
    table.on('tableBuilt', function(){
      console.log("Table built successfully");
      setTimeout(() => initializeDualPagination(), 200);
      // Initialize all event handlers after table is built
      setTimeout(() => initializeAllEventHandlers(), 300);
    });
    
    table.on('paginationInitialized', function(){
      console.log("Pagination initialized");
      setTimeout(() => initializeDualPagination(), 100);
    });
    
    table.on('pageLoaded', function(){
      console.log('Page loaded, checking pagination sync...');
      if (!topPager.hasChildNodes() || topPager.children.length === 0) {
        setTimeout(() => initializeDualPagination(), 50);
      }
    });
  }
  
  // Function to get modified data (filtered + edited)
  window.getModifiedData = function() {
    const filteredData = table.getData("visible"); // Only visible (filtered) rows
    return {
      data: filteredData,
      totalRows: filteredData.length,
      hasChanges: hasChanges,
      changeLog: changeLog,
      timestamp: new Date().toISOString()
    };
  };
  
  // Function to save data to server
  window.saveToServer = function() {
    const modifiedData = window.getModifiedData();
    
    // Show loading state
    const saveBtn = document.querySelector('#save-data-btn');
    if (saveBtn) {
      saveBtn.disabled = true;
      saveBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Saving...';
    }
    
  fetch(apiBase + '/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(modifiedData)
    })
    .then(response => response.json())
    .then(result => {
      console.log('Data saved successfully:', result);
      
      // Reset change tracking
      hasChanges = false;
      changeLog = [];
      
      // Show success message
      if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="bi bi-check-circle"></i> Saved!';
        saveBtn.classList.remove('btn-warning');
        saveBtn.classList.add('btn-success');
        
        // Reset button after 2 seconds
  setTimeout(() => {
          saveBtn.innerHTML = '<i class="bi bi-cloud-upload"></i> Save Data';
          saveBtn.classList.remove('btn-success');
          saveBtn.classList.add('btn-primary');
  }, 2000);
      }
      
      showNotification('Data saved successfully!', 'success');
    })
    .catch(error => {
      console.error('Error saving data:', error);
      
      if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Error';
        saveBtn.classList.remove('btn-warning');
        saveBtn.classList.add('btn-danger');
        
        // Reset button after 3 seconds
        setTimeout(() => {
          saveBtn.innerHTML = '<i class="bi bi-cloud-upload"></i> Save Data';
          saveBtn.classList.remove('btn-danger');
          saveBtn.classList.add('btn-primary');
        }, 3000);
      }
      
      showNotification('Error saving data: ' + error.message, 'error');
    });
  };
  
  // Function to show notifications
  function showNotification(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;
    
    // Add to container or create one
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
      document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Show toast (check if Bootstrap is available)
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
      const bsToast = new bootstrap.Toast(toast);
      bsToast.show();
      
      // Remove from DOM after hiding
      toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
      });
    } else {
      // Fallback: show as alert and auto-hide
      toast.style.display = 'block';
      setTimeout(() => {
        toast.remove();
      }, 3000);
    }
  }

  // return component API
  return { 
    table, 
    refresh: async () => {
      const newData = await fetch(apiBase).then(r=>r.json()); 
      table.setData(newData);
    }, 
    schema, 
    data,
    getModifiedData: window.getModifiedData,
    saveToServer: window.saveToServer
  };
};
