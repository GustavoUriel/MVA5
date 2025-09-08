from flask import Blueprint, jsonify, request, current_app, render_template
from flask_login import login_required, current_user
from ...scripts.logging_config import ErrorLogger
from ...scripts.smart_table import build_schema, build_table_data, save_table
from .. import Dataset, DatasetFile, db
import os

editor_bp = Blueprint('editor', __name__)


@editor_bp.route('/file/<int:file_id>', methods=['GET'])
@login_required
def editor_route(file_id):
  """Editor entry endpoint for a specific dataset file. Enforce ownership: only dataset owner may access these endpoints. Returns 404 if file does not exist. """
  dataset_file = DatasetFile.query.filter_by(id=file_id).first_or_404()
  dataset = Dataset.query.filter_by(id=dataset_file.dataset_id).first()
  if not dataset or dataset.user_id != current_user.id:
    return jsonify({'error': 'Forbidden: You do not have access to this file'}), 403

  # Prefer processed file if present and exists on disk; otherwise use uploaded file
  preferred_path = None
  if getattr(dataset_file, 'processed_file_path', None) and os.path.exists(dataset_file.processed_file_path):
    preferred_path = dataset_file.processed_file_path
  else:
    preferred_path = dataset_file.file_path

  if not os.path.exists(preferred_path):
    return jsonify({'error': 'File not found'}), 404

  # Build apiBase and options for the client-side table component
  # Determine table type for title
  table_type = dataset_file.file_type if hasattr(
      dataset_file, 'file_type') else 'file'
  # For the editor, use the basename of the preferred file
  filename = os.path.basename(preferred_path)
  title = f'Smart-table editor for {table_type.title()} table'
  api_base = request.url_root.rstrip('/') + request.path
  options = {
      "showDebug": True,
      "pageSize": 10,
      "filename": filename,
      "columnConfig": {
          "gender": {
              "displayType": "label",
              "colorScheme": "custom",
              "customColors": {
                  "Male": "#007bff",
                  "Female": "#e83e8c",
                  "Other": "#6c757d",
              },
          },
      },
  }
  return render_template('smart_table.html', title=title, apiBase=api_base, options=options)


@editor_bp.route('/file/<int:file_id>/data', methods=['GET'])
@login_required
def editor_data(file_id):
  dataset_file = DatasetFile.query.filter_by(id=file_id).first_or_404()
  dataset = Dataset.query.filter_by(id=dataset_file.dataset_id).first()
  if not dataset or dataset.user_id != current_user.id:
    return jsonify({'error': 'Forbidden: You do not have access to this file'}), 403

  # Prefer processed file if present
  if getattr(dataset_file, 'processed_file_path', None) and os.path.exists(dataset_file.processed_file_path):
    file_path = dataset_file.processed_file_path
  else:
    file_path = dataset_file.file_path

  if not os.path.exists(file_path):
    return jsonify({'error': 'File not found'}), 404

  return jsonify(build_table_data(csv_file=file_path))


@editor_bp.route('/file/<int:file_id>/schema', methods=['GET'])
@login_required
def editor_schema(file_id):
  dataset_file = DatasetFile.query.filter_by(id=file_id).first_or_404()
  dataset = Dataset.query.filter_by(id=dataset_file.dataset_id).first()
  if not dataset or dataset.user_id != current_user.id:
    return jsonify({'error': 'Forbidden: You do not have access to this file'}), 403

  # Prefer processed file if present
  if getattr(dataset_file, 'processed_file_path', None) and os.path.exists(dataset_file.processed_file_path):
    file_path = dataset_file.processed_file_path
  else:
    file_path = dataset_file.file_path

  if not os.path.exists(file_path):
    return jsonify({'error': 'File not found'}), 404

  return jsonify(build_schema(csv_file=file_path))


@editor_bp.route('/file/<int:file_id>/save', methods=['POST'])
@login_required
def editor_save(file_id):
  dataset_file = DatasetFile.query.filter_by(id=file_id).first_or_404()
  dataset = Dataset.query.filter_by(id=dataset_file.dataset_id).first()
  if not dataset or dataset.user_id != current_user.id:
    return jsonify({'error': 'Forbidden: You do not have access to this file'}), 403

  # Prefer processed file if present when saving edits, otherwise save to uploaded file
  if getattr(dataset_file, 'processed_file_path', None) and os.path.exists(dataset_file.processed_file_path):
    file_path = dataset_file.processed_file_path
  else:
    file_path = dataset_file.file_path

  if not os.path.exists(file_path):
    return jsonify({'error': 'File not found'}), 404

  try:
    data = request.get_json()
    if not data:
      return jsonify({"status": "error", "message": "No data received"}), 400
    save_table(data=data, csv_file=file_path)

    # Recalculate file size after saving
    new_file_size = os.path.getsize(file_path)
    dataset_file.file_size = new_file_size
    dataset_file.update_modified_timestamp()

    # Update dataset total size
    dataset.total_size = sum(f.file_size for f in dataset.files)
    db.session.commit()

    return jsonify({"status": "success", "message": "Data saved successfully"}), 200
  except Exception as e:
    print(f"Error processing request: {str(e)}")
    return jsonify({"status": "error", "message": f"Error processing request: {str(e)}"}), 500
