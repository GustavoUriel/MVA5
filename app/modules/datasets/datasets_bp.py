from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from ...scripts.logging_config import log_user_action, ErrorLogger
from .. import Dataset, DatasetFile, db
from ...file_utils import get_dataset_files_folder
from datetime import datetime
import os
import shutil

datasets_bp = Blueprint('datasets', __name__)


@datasets_bp.route('/dataset/new', methods=['GET', 'POST'])
@login_required
def new_dataset():
  """Create a new dataset"""
  if request.method == 'POST':
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
      flash('Dataset name is required.', 'error')
      return render_template('new_dataset.html')

    # Create new dataset
    dataset = Dataset(
        name=name,
        description=description,
        user_id=current_user.id
    )
    db.session.add(dataset)
    db.session.commit()

    log_user_action(
        "dataset_created",
        f"Dataset: {name}",
        success=True
    )

    flash(f'Dataset "{name}" created successfully!', 'success')
    return redirect(url_for('datasets.view_dataset', dataset_id=dataset.id))

  return render_template('new_dataset.html')


@datasets_bp.route('/dataset/<int:dataset_id>')
@login_required
def view_dataset(dataset_id):
  """View a specific dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  return render_template('dataset.html', dataset=dataset)


@datasets_bp.route('/dataset/<int:dataset_id>/upload', methods=['POST'])
@login_required
def upload_dataset_file(dataset_id):
  """Upload a file to a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    if 'file' not in request.files:
      return jsonify({'success': False, 'message': 'No file provided'}), 400

    file = request.files['file']
    filename_lower = file.filename.lower()
    if file.filename == '':
      return jsonify({'success': False, 'message': 'No file selected'}), 400

    # Determine file type from filename or form data
    file_type = request.form.get('file_type', 'unknown')
    if not file_type or file_type == 'unknown':
      # Try to infer from filename
      if 'patient' in filename_lower or 'patients' in filename_lower:
        file_type = 'patients'
      elif 'taxonomy' in filename_lower:
        file_type = 'taxonomy'
      elif 'bracken' in filename_lower:
        file_type = 'bracken'
      else:
        return jsonify({'success': False, 'message': 'Could not determine file type. Please specify.'}), 400

    # Save file with unique name to avoid conflicts
    from werkzeug.utils import secure_filename
    import time
    show_filename = secure_filename(filename_lower)

    # Create unique filename with timestamp to avoid conflicts
    name_parts = show_filename.rsplit('.', 1)
    timestamp = str(int(time.time()))
    if len(name_parts) == 2:
      base_name = name_parts[0]
      filename = f"{base_name}_{timestamp}"
      show_filename = base_name
    else:
      filename = f"{show_filename}_{timestamp}"
      show_filename = show_filename

    file_path = os.path.join(get_dataset_files_folder(
        current_user.email, dataset_id), file.filename)
    file.save(file_path)

    # Create database record
    dataset_file = DatasetFile(
        dataset_id=dataset_id,
        file_type=file_type,
        show_filename=show_filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path)
    )
    db.session.add(dataset_file)

    # Update dataset status - check if any files of this type exist
    if file_type == 'patients':
      dataset.patients_file_uploaded = True
    elif file_type == 'taxonomy':
      dataset.taxonomy_file_uploaded = True
    elif file_type == 'bracken':
      dataset.bracken_file_uploaded = True

    dataset.file_count = DatasetFile.query.filter_by(
        dataset_id=dataset_id).count() + 1
    dataset.total_size += dataset_file.file_size
    dataset.updated_at = datetime.utcnow()

    db.session.commit()

    log_user_action(
        "file_uploaded",
        f"File: {file.filename} ({file_type}) to dataset '{dataset.name}'",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'{file_type.title()} file uploaded successfully',
        'file_type': file_type,
        'filename': file.filename
    })

  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Uploading file to dataset {dataset_id}",
        user_action=f"User uploading file to dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_type': file_type if 'file_type' in locals() else None,
            'filename': file.filename if 'file' in locals() else None
        }
    )
    log_user_action("file_upload_failed",
                    f"File upload to dataset '{dataset.name}'", success=False)

    return jsonify({
        'success': False,
        'message': f'Error uploading file: {str(e)}'
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/processing-status', methods=['GET'])
@login_required
def get_processing_status(dataset_id):
  """Get processing status for all files in a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  processing_status = {}
  for file in dataset.files:
    processing_status[file.file_type] = {
        'status': file.processing_status,
        'started_at': file.processing_started_at.isoformat() if file.processing_started_at else None,
        'completed_at': file.processing_completed_at.isoformat() if file.processing_completed_at else None,
        'error': file.processing_error,
        'summary': file.processing_summary
    }

  return jsonify({
      'success': True,
      'processing_status': processing_status,
      'dataset_status': {
          'completion_percentage': dataset.completion_percentage,
          'is_complete': dataset.is_complete,
          'status': dataset.status,
          'patients_uploaded': dataset.patients_file_uploaded,
          'taxonomy_uploaded': dataset.taxonomy_file_uploaded,
          'bracken_uploaded': dataset.bracken_file_uploaded,
          'file_count': dataset.file_count,
          'total_size': dataset.total_size
      }
  })


@datasets_bp.route('/dataset/<int:dataset_id>/delete', methods=['POST'])
@login_required
def delete_dataset(dataset_id):
  """Delete a dataset and all its files"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    # Get dataset info for logging
    dataset_name = dataset.name
    file_count = len(dataset.files)
    total_size = sum(f.file_size for f in dataset.files)

    # Delete all associated files from filesystem
    for file in dataset.files:
      if os.path.exists(file.file_path):
        try:
          os.remove(file.file_path)
        except OSError as e:
          ErrorLogger.log_warning(
              f"Could not delete file {file.filename}: {e}",
              context="Dataset deletion",
              user_action=f"User deleting dataset '{dataset.name}'",
              extra_data={'file_path': file.file_path, 'error': str(e)}
          )

    # Delete dataset from database (cascade will delete files)
    db.session.delete(dataset)
    db.session.commit()

    log_user_action(
        "dataset_deleted",
        f"Dataset: {dataset_name} (files: {file_count}, size: {total_size} bytes)",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'Dataset "{dataset_name}" deleted successfully',
        'redirect_url': url_for('main.dashboard')
    })

  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Deleting dataset {dataset_id}",
        user_action=f"User trying to delete dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'dataset_name': dataset.name,
            'file_count': len(dataset.files)
        }
    )
    log_user_action("dataset_deletion_failed",
                    f"Dataset: {dataset.name}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error deleting dataset: {str(e)}'
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/files')
@login_required
def get_dataset_files(dataset_id):
  """Get files for a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  files = []
  for file in dataset.files:
    files.append({
        'id': file.id,
        'file_type': file.file_type,
        'filename': file.show_filename,
        'size': file.file_size,
        'cure_status': file.cure_status,
        'cure_validation_status': file.cure_validation_status,
        'uploaded_at': file.uploaded_at.isoformat(),
        'modified_at': file.modified_at.isoformat()
    })

  return jsonify({
      'files': files,
      'dataset_status': {
          'completion_percentage': dataset.completion_percentage,
          'is_complete': dataset.is_complete,
          'status': dataset.status,
          'patients_uploaded': dataset.patients_file_uploaded,
          'taxonomy_uploaded': dataset.taxonomy_file_uploaded,
          'bracken_uploaded': dataset.bracken_file_uploaded,
          'file_count': dataset.file_count,
          'total_size': dataset.total_size
      }
  })


@datasets_bp.route('/dataset/<int:dataset_id>/data-stats')
@login_required
def get_dataset_data_stats(dataset_id):
  """Get data statistics and analysis for a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    stats = {
        'patients': {},
        'taxonomy': {},
        'bracken': {},
        'cross_references': {},
        'sanitization_needed': []
    }

    # Analyze patients data
    if dataset.patients_file_uploaded:
      patients_file = next(
          (f for f in dataset.files if f.file_type == 'patients'), None)
      if patients_file and patients_file.processed_file_path and os.path.exists(patients_file.processed_file_path):
        import pandas as pd
        df = pd.read_csv(patients_file.processed_file_path)
        stats['patients'] = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'missing_values': df.isnull().sum().to_dict()
        }

    # Analyze taxonomy data
    if dataset.taxonomy_file_uploaded:
      taxonomy_file = next(
          (f for f in dataset.files if f.file_type == 'taxonomy'), None)
      if taxonomy_file and taxonomy_file.processed_file_path and os.path.exists(taxonomy_file.processed_file_path):
        import pandas as pd
        df = pd.read_csv(taxonomy_file.processed_file_path)
        stats['taxonomy'] = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'missing_values': df.isnull().sum().to_dict()
        }

    # Analyze bracken results
    if dataset.bracken_file_uploaded:
      bracken_file = next(
          (f for f in dataset.files if f.file_type == 'bracken'), None)
      if bracken_file and bracken_file.processed_file_path and os.path.exists(bracken_file.processed_file_path):
        import pandas as pd
        df = pd.read_csv(bracken_file.processed_file_path)
        stats['bracken'] = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'missing_values': df.isnull().sum().to_dict()
        }

    # Cross-reference analysis
    if stats['patients'] and stats['taxonomy'] and stats['bracken']:
      try:
        # Simple cross-reference check
        patients_ids = set()
        taxonomy_ids = set()
        bracken_ids = set()

        if 'patient_id' in stats['patients'].get('columns', []):
          patients_df = pd.read_csv(patients_file.processed_file_path)
          patients_ids = set(patients_df['patient_id'].dropna())

        if 'taxonomy_id' in stats['taxonomy'].get('columns', []):
          taxonomy_df = pd.read_csv(taxonomy_file.processed_file_path)
          taxonomy_ids = set(taxonomy_df['taxonomy_id'].dropna())

        if 'taxonomy_id' in stats['bracken'].get('columns', []):
          bracken_df = pd.read_csv(bracken_file.processed_file_path)
          bracken_ids = set(bracken_df['taxonomy_id'].dropna())

        stats['cross_references'] = {
            'patients_taxonomy_overlap': len(patients_ids & taxonomy_ids),
            'taxonomy_bracken_overlap': len(taxonomy_ids & bracken_ids),
            'patients_bracken_overlap': len(patients_ids & bracken_ids),
            'total_patients': len(patients_ids),
            'total_taxonomy': len(taxonomy_ids),
            'total_bracken': len(bracken_ids)
        }

      except Exception as e:
        ErrorLogger.log_warning(
            f"Cross-reference analysis failed: {e}",
            context="Data stats cross-reference",
            user_action=f"User requesting data statistics",
            extra_data={'dataset_id': dataset_id, 'error': str(e)}
        )

    return jsonify({
        'success': True,
        'stats': stats
    })

  except Exception as e:
    ErrorLogger.log_exception(
        e,
        context=f"Getting data stats for dataset {dataset_id}",
        user_action=f"User requesting data statistics",
        extra_data={'dataset_id': dataset_id}
    )
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/sanitize', methods=['POST'])
@login_required
def sanitize_dataset_data(dataset_id):
  """Sanitize dataset data based on identified issues"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    sanitization_type = request.json.get('type')
    file_type = request.json.get('file_type')

    if not sanitization_type or not file_type:
      return jsonify({
          'success': False,
          'message': 'Missing sanitization type or file type'
      }), 400

    # Find the file to sanitize
    file_to_sanitize = next(
        (f for f in dataset.files if f.file_type == file_type), None)
    if not file_to_sanitize or not file_to_sanitize.processed_file_path:
      return jsonify({
          'success': False,
          'message': 'File not found or not processed'
      }), 404

    if not os.path.exists(file_to_sanitize.processed_file_path):
      return jsonify({
          'success': False,
          'message': 'Processed file not found'
      }), 404

    import pandas as pd
    df = pd.read_csv(file_to_sanitize.processed_file_path)
    original_rows = len(df)

    # Apply sanitization based on type
    if sanitization_type == 'remove_duplicates':
      if file_type == 'patients' and 'patient_id' in df.columns:
        df = df.drop_duplicates(subset=['patient_id'])
      elif file_type == 'taxonomy' and 'taxonomy_id' in df.columns:
        df = df.drop_duplicates(subset=['taxonomy_id'])
      elif file_type == 'bracken' and 'taxonomy_id' in df.columns:
        df = df.drop_duplicates(subset=['taxonomy_id'])
      else:
        return jsonify({
            'success': False,
            'message': 'No suitable ID column found for duplicate removal'
        }), 400

    elif sanitization_type == 'remove_missing_ids':
      if file_type == 'patients' and 'patient_id' in df.columns:
        df = df.dropna(subset=['patient_id'])
      elif file_type == 'taxonomy' and 'taxonomy_id' in df.columns:
        df = df.dropna(subset=['taxonomy_id'])
      elif file_type == 'bracken' and 'taxonomy_id' in df.columns:
        df = df.dropna(subset=['taxonomy_id'])
      else:
        return jsonify({
            'success': False,
            'message': 'No suitable ID column found for missing ID removal'
        }), 400

    elif sanitization_type == 'fill_missing_ids':
      if file_type == 'patients' and 'patient_id' in df.columns:
        df['patient_id'] = df['patient_id'].fillna('unknown')
      elif file_type == 'taxonomy' and 'taxonomy_id' in df.columns:
        df['taxonomy_id'] = df['taxonomy_id'].fillna('unknown')
      elif file_type == 'bracken' and 'taxonomy_id' in df.columns:
        df['taxonomy_id'] = df['taxonomy_id'].fillna('unknown')
      else:
        return jsonify({
            'success': False,
            'message': 'No suitable ID column found for filling missing IDs'
        }), 400
    else:
      return jsonify({
          'success': False,
          'message': f'Unknown sanitization type: {sanitization_type}'
      }), 400

    # Save sanitized data
    sanitized_path = file_to_sanitize.processed_file_path.replace(
        '.csv', '_sanitized.csv')
    df.to_csv(sanitized_path, index=False)

    # Update the file record
    file_to_sanitize.processed_file_path = sanitized_path
    file_to_sanitize.processing_summary = f'{{"sanitization_applied": "{sanitization_type}", "original_rows": {original_rows}, "final_rows": {len(df)}, "rows_removed": {original_rows - len(df)}, "sanitized_at": "{datetime.utcnow().isoformat()}"}}'

    db.session.commit()

    log_user_action(
        "data_sanitized",
        f"Dataset: {dataset.name}, File: {file_type}, Type: {sanitization_type}",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'{file_type.title()} data sanitized successfully',
        'details': {
            'original_rows': original_rows,
            'final_rows': len(df),
            'rows_removed': original_rows - len(df),
            'sanitization_type': sanitization_type
        }
    })

  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Sanitizing {file_type} data for dataset {dataset_id}",
        user_action=f"User sanitizing data in dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_type': file_type,
            'sanitization_type': sanitization_type
        }
    )
    return jsonify({
        'success': False,
        'message': f'Error sanitizing data: {str(e)}'
    }), 500
