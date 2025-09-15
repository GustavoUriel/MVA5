from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from ...scripts.logging_config import log_user_action, ErrorLogger
from .. import Dataset, DatasetFile, db
from ...file_utils import get_dataset_files_folder
from datetime import datetime
import os
import shutil
import importlib.util
import json
from collections import OrderedDict

datasets_bp = Blueprint('datasets', __name__)


def load_metadata_module(module_name):
  """Helper function to load metadata modules from the project root"""
  import sys
  import os
  # Add the project root to the Python path
  project_root = os.path.dirname(os.path.dirname(
      os.path.dirname(os.path.dirname(__file__))))
  if project_root not in sys.path:
    sys.path.insert(0, project_root)

  # Import the metadata module
  module = __import__(f'metadata.{module_name}', fromlist=[module_name])
  return getattr(module, module_name)


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
@datasets_bp.route('/dataset/<int:dataset_id>/<tab>')
@login_required
def view_dataset(dataset_id, tab='files'):
  """View a specific dataset with optional tab parameter"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  # Validate tab parameter
  valid_tabs = ['files', 'reports', 'settings']
  if tab not in valid_tabs:
    tab = 'files'

  # Determine which template to render
  template_map = {
      'files': 'dataset/files_tab.html',
      'reports': 'dataset/reports_tab.html',
      'settings': 'dataset/settings_tab.html'
  }

  return render_template(template_map[tab], dataset=dataset, active_tab=tab)


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
      filename = f"{dataset.id}_{show_filename}_{timestamp}"
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


@datasets_bp.route('/dataset/<int:dataset_id>/files/api')
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


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/column-groups')
@login_required
def get_column_groups(dataset_id):
  """Get column groups metadata"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    COLUMN_GROUPS = load_metadata_module('COLUMN_GROUPS')

    # Convert to ordered list to preserve the order from the metadata file
    # Python 3.7+ dictionaries maintain insertion order
    ordered_groups = []
    for group_name, columns in COLUMN_GROUPS.items():
      ordered_groups.append({
          'name': group_name,
          'columns': columns
      })

    return jsonify({
        'success': True,
        'column_groups': ordered_groups
    })
  except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/bracken-time-points')
@login_required
def get_bracken_time_points(dataset_id):
  """Get bracken time points metadata"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    BRACKEN_TIME_POINTS = load_metadata_module('BRACKEN_TIME_POINTS')

    # Convert to ordered list to preserve the order from the metadata file
    # Python 3.7+ dictionaries maintain insertion order
    ordered_time_points = []
    for time_point_key, time_point_data in BRACKEN_TIME_POINTS.items():
      ordered_time_points.append({
          'key': time_point_key,
          'suffix': time_point_data['suffix'],
          'description': time_point_data['description'],
          'timepoint': time_point_data['timepoint'],
          'function': time_point_data['function']
      })

    # Get default time point from the module
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))))
    if project_root not in sys.path:
      sys.path.insert(0, project_root)

    bracken_module = __import__(
        'metadata.BRACKEN_TIME_POINTS', fromlist=['BRACKEN_TIME_POINTS'])
    default_time_point = getattr(bracken_module, 'DEFAULT_TIME_POINT', None)

    return jsonify({
        'success': True,
        'time_points': ordered_time_points,
        'default_time_point': default_time_point
    })
  except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/stratifications')
@login_required
def get_stratifications(dataset_id):
  """Get stratifications metadata"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    STRATIFICATIONS = load_metadata_module('STRATIFICATIONS')

    # Convert to ordered list to preserve the order from the metadata file
    ordered_stratifications = []
    for group_name, group_stratifications in STRATIFICATIONS.items():
      group_data = {
          'group_name': group_name,
          'group_label': format_group_name(group_name),
          'stratifications': []
      }

      for strat_name, strat_data in group_stratifications.items():
        strat_info = {
            'name': strat_name,
            'label': format_stratification_name(strat_name),
            'type': strat_data['type'],
            'method': strat_data['method'],
            'groups': []
        }

        # Add groups information
        if 'groups' in strat_data:
          for group_key, group_info in strat_data['groups'].items():
            strat_info['groups'].append({
                'key': group_key,
                'label': group_info['label']
            })

        # Add parameters for composite stratifications
        if 'parameters' in strat_data:
          strat_info['parameters'] = strat_data['parameters']

        group_data['stratifications'].append(strat_info)

      ordered_stratifications.append(group_data)

    return jsonify({
        'success': True,
        'stratifications': ordered_stratifications
    })
  except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/clustering-methods')
@login_required
def get_clustering_methods(dataset_id):
  """Get clustering methods metadata"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    # Load clustering methods from metadata
    import importlib
    clustering_module = importlib.import_module('metadata.CLUSTERING_METHODS')
    CLUSTERING_METHODS = getattr(clustering_module, 'CLUSTERING_METHODS', {})
    default_method = getattr(
        clustering_module, 'DEFAULT_CLUSTERING_METHOD', 'kmeans')

    return jsonify({
        'success': True,
        'methods': CLUSTERING_METHODS,
        'default_method': default_method
    })
  except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/clustering-methods/<method_name>')
@login_required
def get_clustering_method(dataset_id, method_name):
  """Get specific clustering method metadata"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    CLUSTERING_METHODS = load_metadata_module('CLUSTERING_METHODS')

    if method_name not in CLUSTERING_METHODS:
      return jsonify({
          'success': False,
          'error': f'Clustering method "{method_name}" not found'
      }), 404

    method_data = CLUSTERING_METHODS[method_name]

    return jsonify({
        'success': True,
        'method': method_data
    })
  except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/cluster-representative-methods')
@login_required
def get_cluster_representative_methods(dataset_id):
  """Get cluster representative methods metadata"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))))
    if project_root not in sys.path:
      sys.path.insert(0, project_root)

    cluster_rep_module = __import__('metadata.CLUSTER_REPRESENTATIVE', fromlist=[
                                    'CLUSTER_REPRESENTATIVE_METHODS'])
    CLUSTER_REPRESENTATIVE_METHODS = getattr(
        cluster_rep_module, 'CLUSTER_REPRESENTATIVE_METHODS', {})
    default_method = getattr(
        cluster_rep_module, 'DEFAULT_REPRESENTATIVE_METHOD', None)
    method_categories = getattr(cluster_rep_module, 'METHOD_CATEGORIES', {})

    return jsonify({
        'success': True,
        'cluster_representative_methods': CLUSTER_REPRESENTATIVE_METHODS,
        'default_method': default_method,
        'method_categories': method_categories
    })
  except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/cluster-representative-methods/<method_name>')
@login_required
def get_cluster_representative_method(dataset_id, method_name):
  """Get specific cluster representative method metadata"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))))
    if project_root not in sys.path:
      sys.path.insert(0, project_root)

    cluster_rep_module = __import__('metadata.CLUSTER_REPRESENTATIVE', fromlist=[
                                    'CLUSTER_REPRESENTATIVE_METHODS'])
    CLUSTER_REPRESENTATIVE_METHODS = getattr(
        cluster_rep_module, 'CLUSTER_REPRESENTATIVE_METHODS', {})

    if method_name not in CLUSTER_REPRESENTATIVE_METHODS:
      return jsonify({
          'success': False,
          'error': f'Cluster representative method "{method_name}" not found'
      }), 404

    method_data = CLUSTER_REPRESENTATIVE_METHODS[method_name]

    return jsonify({
        'success': True,
        'method': method_data
    })
  except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


def format_group_name(group_name):
  """Format group name for display"""
  return group_name.replace('_', ' ').title()


def format_stratification_name(strat_name):
  """Format stratification name for display"""
  return strat_name.replace('_', ' ').title()


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

    # Recalculate file size for the new processed file
    if os.path.exists(sanitized_path):
      file_to_sanitize.file_size = os.path.getsize(sanitized_path)

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


@datasets_bp.route('/dataset/<int:dataset_id>/file/<int:file_id>/patient-count')
@login_required
def get_patient_count(dataset_id, file_id):
  """Get patient count from a specific file"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()

  try:
    import pandas as pd
    import os

    # Log file information for debugging
    print(
        f"File ID: {file_id}, File Path: {file.file_path}, Show Filename: {file.show_filename}")

    # Read the file to get patient count
    if not os.path.exists(file.file_path):
      return jsonify({
          'success': False,
          'error': f'File not found at path: {file.file_path}'
      }), 404

    # Read the CSV file
    df = pd.read_csv(file.file_path)

    # Get patient count (assuming first column or a specific patient ID column)
    patient_count = len(df)

    return jsonify({
        'success': True,
        'patient_count': patient_count,
        'file_name': file.show_filename
    })
  except Exception as e:
    print(f"Error in get_patient_count: {str(e)}")
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500




@datasets_bp.route('/metadata/<metadata_type>')
@login_required
def get_metadata(metadata_type):
  """Get metadata configuration dynamically from metadata folder"""
  try:
    # Define the metadata folder path
    metadata_folder = os.path.join(current_app.root_path, '..', 'metadata')

    # Map metadata types to their file names
    metadata_files = {
        'column_groups': 'column_groups.py',
        'time_points': 'BRACKEN_TIME_POINTS.py',
        'analysis_methods': 'ANALYSIS_METHODS.py',
        'clustering_methods': 'CLUSTERING_METHODS.py',
        'grouping_strategies': 'GROUPING_STRATEGIES.py',
        'grouping_analysis_methods': 'GROUPING_ANALYSIS_METHODS.py',
        'kaplan_mayer_variables': 'KAPLAN_MAYER_VARIABLES.py',
        'columns': 'COLUMNS.py'
    }

    if metadata_type not in metadata_files:
      return jsonify({
          'success': False,
          'message': f'Unknown metadata type: {metadata_type}'
      }), 400

    file_path = os.path.join(metadata_folder, metadata_files[metadata_type])

    if not os.path.exists(file_path):
      return jsonify({
          'success': False,
          'message': f'Metadata file not found: {metadata_files[metadata_type]}'
      }), 404

    # Dynamically import the metadata module
    spec = importlib.util.spec_from_file_location(metadata_type, file_path)
    metadata_module = importlib.util.module_from_spec(spec)

    try:
      spec.loader.exec_module(metadata_module)
    except SyntaxError as e:
      return jsonify({
          'success': False,
          'message': f'Syntax error in {metadata_files[metadata_type]}: {str(e)}'
      }), 500
    except Exception as e:
      return jsonify({
          'success': False,
          'message': f'Error executing {metadata_files[metadata_type]}: {str(e)}'
      }), 500

    # Get the main data structure (usually the same name as the file without .py)
    data_key = metadata_files[metadata_type].replace('.py', '').upper()
    metadata_data = getattr(metadata_module, data_key, None)

    if metadata_data is None:
      return jsonify({
          'success': False,
          'message': f'Could not find data structure {data_key} in {metadata_files[metadata_type]}'
      }), 500

    # For time_points, return as ordered list to preserve order
    if metadata_type == 'time_points':
      # Read the file content to extract keys in order
      with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

      # Extract dictionary keys in the order they appear in the file
      import re
      # Find all dictionary keys (quoted strings followed by colon)
      key_pattern = r"'([^']+)'\s*:"
      keys_in_order = re.findall(key_pattern, content)

      # Filter out nested keys (like 'suffix', 'description', etc.) and keep only top-level keys
      # Top-level keys are those that appear at the start of a line (with proper indentation)
      top_level_keys = []
      lines = content.split('\n')
      for line in lines:
        # Look for lines that start with 4 spaces and have a quoted key followed by colon
        if re.match(r'^\s{4}\'([^\']+)\'\s*:\s*\{', line):
          match = re.search(r"'([^']+)'\s*:", line)
          if match:
            key = match.group(1)
            if key not in top_level_keys:
              top_level_keys.append(key)

      keys_in_order = top_level_keys

      # Create ordered data using the keys in file order
      ordered_data = []
      for key in keys_in_order:
        if key in metadata_data:
          ordered_data.append({
              'key': key,
              'value': metadata_data[key]
          })
      return jsonify({
          'success': True,
          'data': ordered_data,
          'is_ordered': True
      })

    return jsonify({
        'success': True,
        'data': metadata_data
    })

  except Exception as e:
    current_app.logger.error(
        f'Error loading metadata {metadata_type}: {str(e)}')
    return jsonify({
        'success': False,
        'message': f'Error loading metadata: {str(e)}'
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/analysis/save', methods=['POST'])
@login_required
def save_analysis_configuration(dataset_id):
  """Save analysis configuration to JSON file"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    data = request.get_json()
    if not data:
      return jsonify({'success': False, 'message': 'No data received'}), 400

    analysis_name = data.get('analysis_name', '').strip()
    analysis_description = data.get('analysis_description', '').strip()
    configuration = data.get('configuration', {})

    if not analysis_name:
      return jsonify({'success': False, 'message': 'Analysis name is required'}), 400

    # Sanitize analysis name for filename
    import re
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', analysis_name)
    # Replace multiple underscores with single
    safe_name = re.sub(r'_+', '_', safe_name)
    safe_name = safe_name.strip('_')  # Remove leading/trailing underscores

    if not safe_name:
      return jsonify({'success': False, 'message': 'Invalid analysis name'}), 400

    # Create analysis folder structure
    user_email = current_user.email.replace('@', '_at_').replace('.', '_dot_')
    analysis_folder = os.path.join(
        current_app.instance_path, 'users', user_email, 'analysis')
    os.makedirs(analysis_folder, exist_ok=True)

    # Create analysis configuration object
    analysis_config = {
        'analysis_name': analysis_name,
        'analysis_description': analysis_description,
        'dataset_id': dataset_id,
        'dataset_name': dataset.name,
        'created_at': datetime.utcnow().isoformat(),
        'created_by': current_user.email,
        'configuration': configuration
    }

    # Save to JSON file
    filename = f"{safe_name}.json"
    filepath = os.path.join(analysis_folder, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
      json.dump(analysis_config, f, indent=2, ensure_ascii=False)

    # Log the action
    log_user_action(
        "analysis_configuration_saved",
        f"Analysis: {analysis_name} (Dataset: {dataset.name})",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'Analysis configuration saved successfully',
        'filename': filename,
        'filepath': filepath
    })

  except Exception as e:
    ErrorLogger.log_exception(
        e,
        context=f"Saving analysis configuration for dataset {dataset_id}",
        user_action=f"User trying to save analysis '{analysis_name}'",
        extra_data={
            'dataset_id': dataset_id,
            'analysis_name': analysis_name,
            'user_email': current_user.email
        }
    )
    log_user_action("analysis_configuration_save_failed",
                    f"Analysis: {analysis_name}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error saving analysis configuration: {str(e)}'
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/analysis/list', methods=['GET'])
@login_required
def list_saved_analyses(dataset_id):
  """List all saved analysis configurations for a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    # Debug log
    print(f"DEBUG: list_saved_analyses called with dataset_id: {dataset_id}")

    # Get user's analysis directory
    user_email = current_user.email.replace('@', '_at_').replace('.', '_dot_')
    analysis_folder = os.path.join(
        current_app.instance_path, 'users', user_email, 'analysis')

    analyses = []

    if os.path.exists(analysis_folder):
      # Scan for JSON files in the analysis directory
      for filename in os.listdir(analysis_folder):
        if filename.endswith('.json'):
          filepath = os.path.join(analysis_folder, filename)
          try:
            with open(filepath, 'r', encoding='utf-8') as f:
              analysis_data = json.load(f)

            # Only include analyses for this dataset
            if analysis_data.get('dataset_id') == dataset_id:
              # Get file stats
              stat = os.stat(filepath)

              analysis_info = {
                  'name': analysis_data.get('analysis_name', 'Unknown'),
                  'description': analysis_data.get('analysis_description', ''),
                  'filename': filename,
                  'created_at': analysis_data.get('created_at', ''),
                  'modified_at': analysis_data.get('modified_at', datetime.fromtimestamp(stat.st_mtime).isoformat()),
                  'size': stat.st_size,
                  'dataset_name': dataset.name,
                  'created_by': current_user.email
              }
              analyses.append(analysis_info)

          except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading analysis file {filename}: {e}")
            continue

    # Sort analyses by modified time (most recent first)
    analyses.sort(key=lambda x: x['modified_at'], reverse=True)

    return jsonify({
        'success': True,
        'analyses': analyses,
        'total': len(analyses)
    })

  except Exception as e:
    ErrorLogger.log_exception(
        e,
        context=f"Listing analyses for dataset {dataset_id}",
        user_action="User trying to list saved analyses"
    )

    return jsonify({
        'success': False,
        'message': f'Error listing analyses: {str(e)}',
        'analyses': [],
        'total': 0
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/analysis/delete', methods=['POST'])
@login_required
def delete_analysis(dataset_id):
  """Delete a saved analysis configuration"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    data = request.get_json()
    if not data or 'filename' not in data:
      return jsonify({'success': False, 'message': 'Filename is required'}), 400

    filename = data['filename']

    # Validate filename (prevent directory traversal)
    if '..' in filename or '/' in filename or '\\' in filename:
      return jsonify({'success': False, 'message': 'Invalid filename'}), 400

    # Get user's analysis directory
    user_email = current_user.email.replace('@', '_at_').replace('.', '_dot_')
    analysis_folder = os.path.join(
        current_app.instance_path, 'users', user_email, 'analysis')
    filepath = os.path.join(analysis_folder, filename)

    # Check if file exists
    if not os.path.exists(filepath):
      return jsonify({'success': False, 'message': 'Analysis file not found'}), 404

    # Delete the file
    os.remove(filepath)

    # Log the action
    log_user_action(
        "analysis_configuration_deleted",
        f"Analysis file: {filename} (Dataset: {dataset.name})",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'Analysis "{filename}" deleted successfully'
    })

  except Exception as e:
    ErrorLogger.log_exception(
        e,
        context=f"Deleting analysis for dataset {dataset_id}",
        user_action=f"User trying to delete analysis '{filename}'",
        extra_data={
            'dataset_id': dataset_id,
            'filename': filename,
            'user_email': current_user.email
        }
    )
    log_user_action("analysis_configuration_delete_failed",
                    f"Analysis file: {filename}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error deleting analysis: {str(e)}'
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/analysis/duplicate', methods=['POST'])
@login_required
def duplicate_analysis(dataset_id):
  """Duplicate a saved analysis configuration"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    data = request.get_json()
    if not data or 'filename' not in data:
      return jsonify({'success': False, 'message': 'Filename is required'}), 400

    filename = data['filename']

    # Validate filename (prevent directory traversal)
    if '..' in filename or '/' in filename or '\\' in filename:
      return jsonify({'success': False, 'message': 'Invalid filename'}), 400

    # Get user's analysis directory
    user_email = current_user.email.replace('@', '_at_').replace('.', '_dot_')
    analysis_folder = os.path.join(
        current_app.instance_path, 'users', user_email, 'analysis')
    original_filepath = os.path.join(analysis_folder, filename)

    # Check if original file exists
    if not os.path.exists(original_filepath):
      return jsonify({'success': False, 'message': 'Analysis file not found'}), 404

    # Create new filename with "_c" suffix
    name_without_ext = filename.replace('.json', '')
    new_filename = f"{name_without_ext}_c.json"
    new_filepath = os.path.join(analysis_folder, new_filename)

    # Ensure the new filename doesn't already exist (add number if needed)
    counter = 1
    while os.path.exists(new_filepath):
      new_filename = f"{name_without_ext}_c{counter}.json"
      new_filepath = os.path.join(analysis_folder, new_filename)
      counter += 1

    # Read original file content
    with open(original_filepath, 'r', encoding='utf-8') as f:
      content = f.read()

    # Write to new file
    with open(new_filepath, 'w', encoding='utf-8') as f:
      f.write(content)

    # Log the action
    log_user_action(
        "analysis_configuration_duplicated",
        f"Original: {filename}, Duplicate: {new_filename} (Dataset: {dataset.name})",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'Analysis duplicated successfully',
        'new_filename': new_filename
    })

  except Exception as e:
    ErrorLogger.log_exception(
        e,
        context=f"Duplicating analysis for dataset {dataset_id}",
        user_action=f"User trying to duplicate analysis '{filename}'",
        extra_data={
            'dataset_id': dataset_id,
            'filename': filename,
            'user_email': current_user.email
        }
    )
    log_user_action("analysis_configuration_duplicate_failed",
                    f"Analysis file: {filename}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error duplicating analysis: {str(e)}'
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/analysis/rename', methods=['POST'])
@login_required
def rename_analysis(dataset_id):
  """Rename a saved analysis configuration (updates the name property, not filename)"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    data = request.get_json()
    if not data or 'filename' not in data or 'new_name' not in data:
      return jsonify({'success': False, 'message': 'Filename and new_name are required'}), 400

    filename = data['filename']
    new_name = data['new_name'].strip()

    if not new_name:
      return jsonify({'success': False, 'message': 'New name cannot be empty'}), 400

    # Validate filename (prevent directory traversal)
    if '..' in filename or '/' in filename or '\\' in filename:
      return jsonify({'success': False, 'message': 'Invalid filename'}), 400

    # Get user's analysis directory
    user_email = current_user.email.replace('@', '_at_').replace('.', '_dot_')
    analysis_folder = os.path.join(
        current_app.instance_path, 'users', user_email, 'analysis')
    filepath = os.path.join(analysis_folder, filename)

    # Check if file exists
    if not os.path.exists(filepath):
      return jsonify({'success': False, 'message': 'Analysis file not found'}), 404

    # Read the JSON file
    with open(filepath, 'r', encoding='utf-8') as f:
      analysis_data = json.load(f)

    # Update the name property (analysis_name field in JSON)
    old_name = analysis_data.get('analysis_name', '')
    analysis_data['analysis_name'] = new_name

    # Remove any duplicate 'name' field if it exists (cleanup from previous versions)
    if 'name' in analysis_data:
      del analysis_data['name']

    # Update the modified timestamp
    from datetime import datetime
    analysis_data['modified_at'] = datetime.now().isoformat()

    # Write the updated JSON back to the file
    with open(filepath, 'w', encoding='utf-8') as f:
      json.dump(analysis_data, f, indent=2, ensure_ascii=False)

    # Log the action
    log_user_action(
        "analysis_configuration_renamed",
        f"Analysis file: {filename}, Name: '{old_name}' → '{new_name}' (Dataset: {dataset.name})",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'Analysis renamed successfully',
        'old_name': old_name,
        'new_name': new_name
    })

  except json.JSONDecodeError as e:
    return jsonify({
        'success': False,
        'message': f'Invalid JSON format in analysis file: {str(e)}'
    }), 400

  except Exception as e:
    ErrorLogger.log_exception(
        e,
        context=f"Renaming analysis for dataset {dataset_id}",
        user_action=f"User trying to rename analysis '{filename}' to '{new_name}'",
        extra_data={
            'dataset_id': dataset_id,
            'filename': filename,
            'new_name': new_name,
            'user_email': current_user.email
        }
    )
    log_user_action("analysis_configuration_rename_failed",
                    f"Analysis file: {filename}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error renaming analysis: {str(e)}'
    }), 500
