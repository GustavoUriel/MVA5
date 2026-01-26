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
  valid_tabs = ['files', 'analysis', 'reports', 'settings']
  if tab not in valid_tabs:
    tab = 'files'

  # Determine which template to render
  template_map = {
      'files': 'dataset/files_tab.html',
      'analysis': 'dataset/analysis_tab.html',
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
    show_filename = secure_filename(filename_lower)

    # Get the file folder path
    file_folder = get_dataset_files_folder(current_user.email, dataset_id)
    file_folder = str(file_folder) if file_folder is not None else ""

    # Extract base name and extension
    name_parts = show_filename.rsplit('.', 1)
    if len(name_parts) == 2:
      base_name = name_parts[0]
      extension = name_parts[1]
    else:
      base_name = show_filename
      extension = ''

    # Check if a file with the same name already exists in the files folder
    # If it does, append a numeral (1, 2, 3, etc.) until we find a unique name
    final_filename = show_filename
    counter = 1
    file_path = os.path.join(file_folder, final_filename)
    while os.path.exists(file_path):
      # Construct new filename with numeral
      if extension:
        final_filename = f"{base_name}_{counter}.{extension}"
      else:
        final_filename = f"{base_name}_{counter}"
      file_path = os.path.join(file_folder, final_filename)
      counter += 1

    # Save the file with the final filename
    file.save(file_path)
    
    # Update show_filename to match the final filename used
    show_filename = final_filename

    # Create database record
    dataset_file = DatasetFile(
        dataset_id=dataset_id,
        file_type=file_type,
        show_filename=show_filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path)
    )
    db.session.add(dataset_file)

    # Update dataset status flags based on actual files
    dataset.update_file_status_flags()

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


@datasets_bp.route('/dataset/<int:dataset_id>/file/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_dataset_file(dataset_id, file_id):
  """Delete a specific file from a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  
  file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()
  
  try:
    # Get file info for logging
    filename = file.show_filename
    file_type = file.file_type
    file_size = file.file_size
    
    # Delete file from filesystem
    if os.path.exists(file.file_path):
      try:
        os.remove(file.file_path)
      except OSError as e:
        ErrorLogger.log_warning(
            f"Could not delete file {file.file_path}: {e}",
            context="File deletion",
            user_action=f"User deleting file '{filename}' from dataset '{dataset.name}'",
            extra_data={'file_path': file.file_path, 'error': str(e)}
        )
    
    # Delete file from database
    db.session.delete(file)
    
    # Update dataset status flags based on remaining files
    dataset.update_file_status_flags()
    
    # Update dataset file count and total size
    dataset.file_count = DatasetFile.query.filter_by(dataset_id=dataset_id).count()
    dataset.total_size = sum(f.file_size for f in dataset.files)
    dataset.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    log_user_action(
        "file_deleted",
        f"File: {filename} ({file_type}) from dataset '{dataset.name}'",
        success=True
    )
    
    return jsonify({
        'success': True,
        'message': f'File "{filename}" deleted successfully'
    })
    
  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Deleting file {file_id} from dataset {dataset_id}",
        user_action=f"User trying to delete file '{file.show_filename}' from dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_id': file_id,
            'filename': file.show_filename
        }
    )
    log_user_action("file_deletion_failed",
                    f"File: {file.show_filename} from dataset '{dataset.name}'", success=False)
    
    return jsonify({
        'success': False,
        'message': f'Error deleting file: {str(e)}'
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/files/<int:file_id>/duplicate', methods=['POST'])
@login_required
def duplicate_dataset_file(dataset_id, file_id):
  """Duplicate a specific file in a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  
  file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()
  
  try:
    # Get original file info
    original_filename = file.show_filename
    original_file_path = file.file_path
    file_type = file.file_type
    
    # Create new filename with "_copy" suffix
    name_parts = original_filename.rsplit('.', 1)
    if len(name_parts) == 2:
      base_name = name_parts[0]
      extension = name_parts[1]
      new_filename = f"{base_name}_copy.{extension}"
    else:
      new_filename = f"{original_filename}_copy"
    
    # Ensure the new filename doesn't already exist
    counter = 1
    temp_filename = new_filename
    while DatasetFile.query.filter_by(dataset_id=dataset_id, show_filename=temp_filename).first():
      name_parts = new_filename.rsplit('.', 1) if '.' in new_filename else [new_filename, '']
      if name_parts[1]:
        temp_filename = f"{name_parts[0]}_{counter}.{name_parts[1]}"
      else:
        temp_filename = f"{name_parts[0]}_{counter}"
      counter += 1
    new_filename = temp_filename
    
    # Copy the file in filesystem
    new_file_path = original_file_path.rsplit('.', 1)
    if len(new_file_path) == 2:
      new_file_path = f"{new_file_path[0]}_copy.{new_file_path[1]}"
    else:
      new_file_path = f"{original_file_path}_copy"
    
    # Ensure unique file path
    counter = 1
    temp_file_path = new_file_path
    while os.path.exists(temp_file_path):
      path_parts = new_file_path.rsplit('.', 1) if '.' in new_file_path else [new_file_path, '']
      if path_parts[1]:
        temp_file_path = f"{path_parts[0]}_{counter}.{path_parts[1]}"
      else:
        temp_file_path = f"{path_parts[0]}_{counter}"
      counter += 1
    new_file_path = temp_file_path
    
    # Copy the file
    shutil.copy2(original_file_path, new_file_path)
    
    # Create new database record
    new_file = DatasetFile(
        dataset_id=dataset_id,
        file_type=file_type,
        show_filename=new_filename,
        file_path=new_file_path,
        file_size=os.path.getsize(new_file_path)
    )
    db.session.add(new_file)
    
    # Update dataset file count and total size
    dataset.file_count = DatasetFile.query.filter_by(dataset_id=dataset_id).count() + 1
    dataset.total_size += new_file.file_size
    dataset.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    log_user_action(
        "file_duplicated",
        f"File: {original_filename} → {new_filename} in dataset '{dataset.name}'",
        success=True
    )
    
    return jsonify({
        'success': True,
        'message': f'File "{original_filename}" duplicated successfully as "{new_filename}"'
    })
    
  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Duplicating file {file_id} in dataset {dataset_id}",
        user_action=f"User trying to duplicate file '{file.show_filename}' in dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_id': file_id,
            'filename': file.show_filename
        }
    )
    log_user_action("file_duplication_failed",
                    f"File: {file.show_filename} in dataset '{dataset.name}'", success=False)
    
    return jsonify({
        'success': False,
        'message': f'Error duplicating file: {str(e)}'
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/files/<int:file_id>/rename', methods=['POST'])
@login_required
def rename_dataset_file(dataset_id, file_id):
  """Rename a specific file in a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  
  file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()
  
  try:
    data = request.get_json()
    if not data or 'new_filename' not in data:
      return jsonify({'success': False, 'message': 'New filename is required'}), 400
    
    new_filename = data['new_filename'].strip()
    if not new_filename:
      return jsonify({'success': False, 'message': 'New filename cannot be empty'}), 400
    
    # Validate filename (prevent directory traversal and invalid characters)
    if '..' in new_filename or '/' in new_filename or '\\' in new_filename:
      return jsonify({'success': False, 'message': 'Invalid filename'}), 400
    
    # Check if filename already exists
    existing_file = DatasetFile.query.filter_by(
        dataset_id=dataset_id, show_filename=new_filename).first()
    if existing_file and existing_file.id != file_id:
      return jsonify({'success': False, 'message': 'A file with this name already exists'}), 400
    
    # Get old filename for logging
    old_filename = file.show_filename
    
    # Update the database record
    file.show_filename = new_filename
    file.modified_at = datetime.utcnow()
    
    db.session.commit()
    
    log_user_action(
        "file_renamed",
        f"File: {old_filename} → {new_filename} in dataset '{dataset.name}'",
        success=True
    )
    
    return jsonify({
        'success': True,
        'message': f'File renamed successfully',
        'new_filename': new_filename
    })
    
  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Renaming file {file_id} in dataset {dataset_id}",
        user_action=f"User trying to rename file '{file.show_filename}' in dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_id': file_id,
            'new_filename': request.get_json().get('new_filename') if request.get_json() else None
        }
    )
    log_user_action("file_rename_failed",
                    f"File: {file.show_filename} in dataset '{dataset.name}'", success=False)
    
    return jsonify({
        'success': False,
        'message': f'Error renaming file: {str(e)}'
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/files/<int:file_id>', methods=['DELETE'])
@login_required
def delete_dataset_file_alt(dataset_id, file_id):
  """Delete a specific file from a dataset (alternative route for frontend compatibility)"""
  return delete_dataset_file(dataset_id, file_id)


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
        'relative_path': os.path.basename(file.file_path),
        'curate_status': file.curated,
        'curate_validation_status': file.curated_validation_status,
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

    # Convert to array format for frontend with all data from source file
    column_groups_array = []
    for group_key, value in COLUMN_GROUPS.items():
      if isinstance(value, dict):
        # Copy all fields from the dict, and add group_key for reference
        group_obj = dict(value)
        group_obj['group_key'] = group_key
      else:
        # If value is just a list, wrap in dict with columns and group_key
        group_obj = {
          'columns': value if value is not None else [],
          'group_key': group_key
        }
      column_groups_array.append(group_obj)

    return jsonify({
        'success': True,
        'column_groups': column_groups_array
    })
  except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/attribute-discarding')
@login_required
def get_attribute_discarding_policies(dataset_id):

  """Get attribute discarding policies metadata"""
  try:
    ATTRIBUTE_DISCARDING = load_metadata_module('ATTRIBUTE_DISCARDING')

    # Convert to array format for frontend with all data from source file
    discarding_policies_array = []
    for policy_key, policy_data in ATTRIBUTE_DISCARDING.items():
      policy_obj = dict(policy_data)
      policy_obj['policy_key'] = policy_key
      discarding_policies_array.append(policy_obj)

    return jsonify({
        'success': True,
        'attribute_discarding_policies': discarding_policies_array
    })
  except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/attribute-discarding/calculate-remaining', methods=['POST'])
@login_required
def calculate_remaining_attributes(dataset_id):
  """Calculate how many attributes remain after applying discarding policies"""
  try:
    # For now, return placeholder message as requested
    return jsonify({
        'success': False,
        'message': 'Calculation of remaining attributes not yet implemented'
    }), 501

  except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/microbial-discarding')
@login_required
def get_microbial_discarding_policies(dataset_id):
  """Get microbial discarding policies metadata"""

  try:
    MICROBIAL_DISCARDING = load_metadata_module('MICROBIAL_DISCARDING')

    # Convert to array format for frontend with all data from source file
    discarding_policies_array = []
    for policy_key, policy_data in MICROBIAL_DISCARDING.items():
      if policy_key != 'DEFAULT_MICROBIAL_DISCARDING_SETTINGS':  # Skip the default settings
        policy_obj = dict(policy_data)
        policy_obj['policy_key'] = policy_key
        discarding_policies_array.append(policy_obj)

    return jsonify({
        'success': True,
        'microbial_discarding_policies': discarding_policies_array
    })
  except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/microbial-discarding/calculate-remaining', methods=['POST'])
@login_required
def calculate_remaining_microbes(dataset_id):
  """Calculate how many microbial taxa remain after applying discarding policies"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    # For now, return placeholder message as requested
    return jsonify({
        'success': False,
        'message': 'Calculation of remaining microbial taxa not yet implemented'
    }), 501

  except Exception as e:
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/microbial-grouping')
@login_required
def get_microbial_grouping_methods(dataset_id):
  """Get microbial grouping methods metadata"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()


  try:
    MICROBIAL_GROUPING = load_metadata_module('MICROBIAL_GROUPING')

    # Convert to array format for frontend with all data from source file
    grouping_methods_array = []
    for method_key, method_data in MICROBIAL_GROUPING.items():
      if method_key != 'DEFAULT_MICROBIAL_GROUPING_SETTINGS':  # Skip the default settings
        method_obj = dict(method_data)
        method_obj['method_key'] = method_key
        grouping_methods_array.append(method_obj)

    return jsonify({
        'success': True,
        'microbial_grouping_methods': grouping_methods_array
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
  try:
    # Load stratifications from metadata
    import importlib
    stratifications_module = importlib.import_module('metadata.POPULATION_STRATIFICATIONS')
    POPULATION_STRATIFICATIONS = getattr(stratifications_module, 'POPULATION_STRATIFICATIONS', {})
    default_stratification = getattr(stratifications_module, 'DEFAULT_STRATIFICATION', None)

    # Convert to array format for frontend with all data from source file
    stratifications_array = []
    for stratification_key, stratification_data in POPULATION_STRATIFICATIONS.items():
      if stratification_key != 'DEFAULT_POPULATION_STRATIFICATIONS_SETTINGS':  # Skip the default settings
        stratification_obj = dict(stratification_data)
        stratification_obj['stratification_key'] = stratification_key
        stratifications_array.append(stratification_obj)

    return jsonify({
        'success': True,
        'stratifications': stratifications_array,
        'default_stratification': default_stratification
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
  try:
    # Load clustering methods from metadata
    import importlib
    clustering_module = importlib.import_module('metadata.CLUSTERING_METHODS')
    CLUSTERING_METHODS = getattr(clustering_module, 'CLUSTERING_METHODS', {})
    default_method = getattr(
        clustering_module, 'DEFAULT_CLUSTERING_METHOD', None)

    # Convert to array format for frontend with all data from source file
    clustering_methods_array = []
    for method_key, method_data in CLUSTERING_METHODS.items():
      method_obj = dict(method_data)
      method_obj['method_key'] = method_key
      clustering_methods_array.append(method_obj)

    return jsonify({
        'success': True,
        'clustering_methods': clustering_methods_array,
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

    # Convert to array format for frontend with all data from source file
    cluster_representative_methods_array = []
    for method_key, method_data in CLUSTER_REPRESENTATIVE_METHODS.items():
      method_obj = dict(method_data)
      method_obj['method_key'] = method_key
      cluster_representative_methods_array.append(method_obj)

    return jsonify({
        'success': True,
        'cluster_representative_methods': cluster_representative_methods_array,
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
  """Get patient count from a specific file (by file ID)"""
  dataset = Dataset.query.filter_by(
    id=dataset_id, user_id=current_user.id).first_or_404()

  # Query file directly by ID and dataset_id
  file = DatasetFile.query.filter_by(
    id=file_id, dataset_id=dataset_id
  ).first_or_404()

  try:
    import pandas as pd

    # Log file information for debugging (show both original and processed paths)
    current_app.logger.debug(
      f"File ID: {file_id}, File Path: {file.file_path}, Processed Path: {getattr(file, 'processed_file_path', None)}, Show Filename: {file.show_filename}")

    # Prefer processed file path when available (some workflows write a processed file)
    file_path_to_use = file.processed_file_path if getattr(
        file, 'processed_file_path', None) else file.file_path

    # Read the file to get patient count
    if not os.path.exists(file_path_to_use):
      # Try fallback: the DB may have stored a path with an old base; construct
      # the expected path under the app instance using get_dataset_files_folder
      fallback_dir = get_dataset_files_folder(current_user.email, dataset_id)
      fallback_path = os.path.join(fallback_dir, os.path.basename(
          file_path_to_use)) if fallback_dir else None

      if fallback_path and os.path.exists(fallback_path):
        current_app.logger.info(
            f"Using fallback path for patient-count: {fallback_path}")
        file_path_to_use = fallback_path
      else:
        current_app.logger.warning(
            f"Patient count file not found. Tried: {file_path_to_use} and fallback: {fallback_path}")
        return jsonify({
            'success': False,
            'error': f'File not found at path: {file_path_to_use}'
        }), 404

    # Read the CSV file
    df = pd.read_csv(file_path_to_use)

    # Get patient count (assuming first column or a specific patient ID column)
    patient_count = len(df)

    return jsonify({
        'success': True,
        'patient_count': patient_count,
        'file_name': file.show_filename
    })
  except Exception as e:
    current_app.logger.exception(f"Error in get_patient_count: {str(e)}")
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/bracken-time-points')
@login_required
def get_bracken_time_points(dataset_id):
  """Get all bracken time points"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    # Load bracken time points from metadata
    bracken_time_points = load_metadata_module('BRACKEN_TIME_POINTS')

    # Get default time point
    import importlib
    time_points_module = importlib.import_module('metadata.BRACKEN_TIME_POINTS')
    default_time_point = getattr(time_points_module, 'DEFAULT_TIME_POINT', 'pre')

    # Convert to array format for frontend
    time_points_array = []
    for key, value in bracken_time_points.items():
      time_point_data = dict(value)
      time_point_data['key'] = key
      time_points_array.append(time_point_data)

    return jsonify({
        'success': True,
        'bracken_time_points': time_points_array,
        'default_time_point': default_time_point
    })
  except Exception as e:
    current_app.logger.exception(f"Error loading bracken time points: {str(e)}")
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/analysis-methods')
@login_required
def get_analysis_methods(dataset_id):
  """Get all analysis methods and default method"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    # Load analysis methods from metadata
    analysis_methods = load_metadata_module('ANALYSIS_METHODS')

    # Get default method and categories
    import importlib
    analysis_module = importlib.import_module('metadata.ANALYSIS_METHODS')
    default_method = getattr(
        analysis_module, 'DEFAULT_ANALYSIS_METHOD', 'cox_proportional_hazards')
    method_categories = getattr(analysis_module, 'METHOD_CATEGORIES', {})
    method_descriptions = getattr(analysis_module, 'METHOD_DESCRIPTIONS', {})

    # Convert to array format for frontend with all data from source file
    analysis_methods_array = []
    for method_key, method_data in analysis_methods.items():
      method_obj = dict(method_data)
      method_obj['method_key'] = method_key
      analysis_methods_array.append(method_obj)

    return jsonify({
        'success': True,
        'analysis_methods': analysis_methods_array,
        'default_method': default_method,
        'categories': method_categories,
        'descriptions': method_descriptions
    })
  except Exception as e:
    current_app.logger.exception(f"Error loading analysis methods: {str(e)}")
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500


@datasets_bp.route('/dataset/<int:dataset_id>/metadata/analysis-methods/<method_name>')
@login_required
def get_analysis_method(dataset_id, method_name):
  """Get details for a specific analysis method"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()

  try:
    # Load analysis methods from metadata
    analysis_methods = load_metadata_module('ANALYSIS_METHODS')

    if method_name not in analysis_methods:
      return jsonify({
          'success': False,
          'error': f'Analysis method "{method_name}" not found'
      }), 404

    method_details = analysis_methods[method_name]

    return jsonify({
        'success': True,
        'method': method_details
    })
  except Exception as e:
    current_app.logger.exception(
        f"Error loading analysis method {method_name}: {str(e)}")
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
        current_app.instance_path, 'users', user_email, str(dataset_id), 'analysis')
    os.makedirs(analysis_folder, exist_ok=True)

    # Optionally include full DOM snapshot if provided
    full_dom = data.get('full_dom') if isinstance(data, dict) else None

    # Create analysis configuration object
    analysis_config = {
      'analysis_name': analysis_name,
      'analysis_description': analysis_description,
      'dataset_id': dataset_id,
      'dataset_name': dataset.name,
      'created_at': datetime.utcnow().isoformat(),
      'modified_at': datetime.utcnow().isoformat(),
      # relative path from instance (use a stable, portable relative path)
      'relative_path': f"users/{user_email}/{dataset_id}/analysis/{safe_name}.json",
      # last_run is null until the analysis is executed; run_status is null when never run
      'last_run': None,
      'run_status': None,
      'created_by': current_user.email,
      'configuration': configuration
    }

    if full_dom is not None:
      # Persist the full DOM snapshot into the JSON
      analysis_config['full_dom'] = full_dom

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
    current_app.logger.debug(
        f"DEBUG: list_saved_analyses called with dataset_id: {dataset_id}")

    # Get user's analysis directory
    user_email = current_user.email.replace('@', '_at_').replace('.', '_dot_')
    analysis_folder = os.path.join(
        current_app.instance_path, 'users', user_email, str(dataset_id), 'analysis')

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
                  'relative_path': analysis_data.get('relative_path', None),
                  'last_run': analysis_data.get('last_run', None),
                  'run_status': analysis_data.get('run_status', None),
                  'filename': filename,
                  'created_at': analysis_data.get('created_at', ''),
                  'modified_at': analysis_data.get('modified_at', datetime.fromtimestamp(stat.st_mtime).isoformat()),
                  'size': stat.st_size,
                  'dataset_name': dataset.name,
                  'created_by': current_user.email
              }
              analyses.append(analysis_info)

          except (json.JSONDecodeError, IOError) as e:
            current_app.logger.warning(
                f"Error reading analysis file {filename}: {e}")
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
        current_app.instance_path, 'users', user_email, str(dataset_id), 'analysis')
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
        current_app.instance_path, 'users', user_email, str(dataset_id), 'analysis')
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

    # Read original file content and update fields for duplicate
    with open(original_filepath, 'r', encoding='utf-8') as f:
      try:
        original_data = json.load(f)
      except Exception:
        # Fallback: copy raw content if JSON parse fails
        f.seek(0)
        content = f.read()
        with open(new_filepath, 'w', encoding='utf-8') as out_f:
          out_f.write(content)
      else:
        # Reset run state for duplicate and update created_at/created_by/relative_path
        original_data['created_at'] = datetime.utcnow().isoformat()
        original_data['created_by'] = current_user.email
        original_data['modified_at'] = datetime.utcnow().isoformat()
        original_data['last_run'] = None
        original_data['run_status'] = None
        original_data['dataset_id'] = dataset_id
        # Update the relative_path to the new filename
        original_data['relative_path'] = f"users/{user_email}/{dataset_id}/analysis/{new_filename}"
        with open(new_filepath, 'w', encoding='utf-8') as out_f:
          json.dump(original_data, out_f, indent=2, ensure_ascii=False)

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
        current_app.instance_path, 'users', user_email, str(dataset_id), 'analysis')
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

    # Update the modified timestamp (do not change run_status/last_run)
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
