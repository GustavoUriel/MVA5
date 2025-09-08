from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from ...scripts.logging_config import log_user_action, ErrorLogger
from .. import Dataset, DatasetFile, db
from datetime import datetime
import os
import shutil

files_bp = Blueprint('files', __name__)


@files_bp.route('/dataset/<int:dataset_id>/file/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_dataset_file(dataset_id, file_id):
  """Delete a specific file from a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  dataset_file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()

  try:
    # Get file info for logging
    file_type = dataset_file.file_type
    filename = dataset_file.show_filename
    file_size = dataset_file.file_size

    # Delete the physical file
    if os.path.exists(dataset_file.file_path):
      try:
        os.remove(dataset_file.file_path)
      except OSError as e:
        ErrorLogger.log_warning(
            f"Could not delete file {dataset_file.filename}: {e}",
            context="Individual file deletion",
            user_action=f"User deleting file '{filename}' from dataset '{dataset.name}'",
            extra_data={'file_path': file_path, 'error': str(e)}
        )

    # Also delete processed file if it exists
    if dataset_file.processed_file_path and os.path.exists(dataset_file.processed_file_path):
      try:
        os.remove(dataset_file.processed_file_path)
      except OSError as e:
        ErrorLogger.log_warning(
            f"Could not delete processed file {dataset_file.processed_file_path}: {e}",
            context="Individual file deletion",
            user_action=f"User deleting file '{filename}' from dataset '{dataset.name}'",
            extra_data={
                'file_path': dataset_file.processed_file_path, 'error': str(e)}
        )

    # Update dataset file status flags - only reset if no files of this type remain
    remaining_files_of_type = [
        f for f in dataset.files if f.id != file_id and f.file_type == file_type]
    if not remaining_files_of_type:
      if file_type == 'patients':
        dataset.patients_file_uploaded = False
      elif file_type == 'taxonomy':
        dataset.taxonomy_file_uploaded = False
      elif file_type == 'bracken':
        dataset.bracken_file_uploaded = False

    # Update dataset status
    if not dataset.is_complete:
      dataset.status = 'draft'

    dataset.updated_at = datetime.utcnow()

    # Delete the database record
    db.session.delete(dataset_file)
    db.session.commit()

    # Refresh the dataset to get updated file count and total size
    db.session.refresh(dataset)

    # Update file count and total size
    dataset.file_count = len(dataset.files)
    dataset.total_size = sum(f.file_size for f in dataset.files)
    db.session.commit()

    log_user_action(
        "file_deleted",
        f"File deleted: {filename} ({file_type}) from dataset '{dataset.name}'",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'{file_type.title()} file "{filename}" deleted successfully',
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

  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Deleting file {file_id} from dataset {dataset_id}",
        user_action=f"User trying to delete file from dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_id': file_id,
            'file_type': dataset_file.file_type,
            'filename': dataset_file.show_filename
        }
    )
    log_user_action("file_deletion_failed",
                    f"File: {dataset_file.show_filename}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error deleting file: {str(e)}'
    }), 500


@files_bp.route('/dataset/<int:dataset_id>/file/<int:file_id>/duplicate', methods=['POST'])
@login_required
def duplicate_dataset_file(dataset_id, file_id):
  """Duplicate a specific file in a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  dataset_file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()

  try:
    # Get file info
    show_filename = dataset_file.show_filename
    file_type = dataset_file.file_type
    file_size = dataset_file.file_size

    # Generate new filename with "_copy" suffix
    name_parts = show_filename.rsplit('.', 1)
    if len(name_parts) == 2:
      base_name, extension = name_parts
      new_show_filename = f"{base_name}_copy.{extension}"
    else:
      new_show_filename = f"{show_filename}_copy"

    # Generate new internal filename
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{dataset.id}_{file_type}_{timestamp}_copy{os.path.splitext(show_filename)[1]}"

    # Copy the physical file (handle missing file gracefully)
    original_file_path = dataset_file.file_path
    # Always add .csv extension to the duplicated file
    new_file_path = os.path.join(
        os.path.dirname(
            original_file_path), f"{os.path.splitext(new_filename)[0]}.csv"
    )

    if not os.path.exists(original_file_path):
      # Return 404 instead of raising so callers get a clean response
      ErrorLogger.log_warning(
          f"Original file not found when duplicating: {original_file_path}",
          context="File duplication",
          user_action=f"User trying to duplicate file '{show_filename}' in dataset '{dataset.name}'",
          extra_data={'dataset_id': dataset_id, 'file_id': file_id}
      )
      return jsonify({'success': False, 'message': 'Original file not found'}), 404

    try:
      shutil.copy2(original_file_path, new_file_path)
    except Exception as e:
      db.session.rollback()
      ErrorLogger.log_exception(
          e,
          context="Copying file during duplication",
          user_action=f"User duplicating file '{show_filename}' in dataset '{dataset.name}'",
          extra_data={'src': original_file_path, 'dst': new_file_path}
      )
      log_user_action("file_duplication_failed",
                      f"File copy failed: {show_filename}", success=False)
      return jsonify({'success': False, 'message': f'Error copying file: {str(e)}'}), 500

    # Create new database entry with optimized fields
    new_dataset_file = DatasetFile(
        dataset_id=dataset_file.dataset_id,
        file_type=dataset_file.file_type,
        show_filename=dataset_file.show_filename + "_c",
        file_size=dataset_file.file_size,
        upload_method='duplicate',
        file_path=new_file_path,
        processing_status='completed',  # ✅ Optimized: Skip processing for duplicates
        processing_summary=None,  # ✅ Optimized: No processing summary needed
        cure_status='not_cured',  # ✅ Optimized: Reset cure status
        cure_validation_status='pending',  # ✅ Optimized: Reset validation
        uploaded_at=dataset_file.uploaded_at,
        modified_at=datetime.utcnow()
    )

    db.session.add(new_dataset_file)

    # Update dataset statistics in a single transaction
    dataset.updated_at = datetime.utcnow()
    dataset.file_count = len(dataset.files) + 1  # ✅ Optimized: Avoid recounting
    # ✅ Optimized: Avoid recounting
    dataset.total_size = sum(f.file_size for f in dataset.files) + file_size

    db.session.commit()  # ✅ Single commit for both operations

    log_user_action(
        "file_duplicated",
        f"File duplicated: {show_filename} -> {new_show_filename} in dataset '{dataset.name}'",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'File "{show_filename}" duplicated successfully as "{new_show_filename}"',
        'file_type': file_type,
        'show_filename': show_filename,
        'new_filename': new_show_filename,
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

  except Exception as e:
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Duplicating file {file_id} from dataset {dataset_id}",
        user_action=f"User trying to duplicate file from dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_id': file_id,
            'file_type': dataset_file.file_type,
            'filename': dataset_file.show_filename
        }
    )
    log_user_action("file_duplication_failed",
                    f"File: {dataset_file.show_filename}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error duplicating file: {str(e)}'
    }), 500


@files_bp.route('/dataset/<int:dataset_id>/file/<int:file_id>/cure', methods=['POST'])
@login_required
def cure_dataset_file(dataset_id, file_id):
  """Cure (process and validate) a specific file in a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  dataset_file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()

  try:
    # Update cure status to curing
    dataset_file.cure_status = 'curing'
    db.session.commit()

    # Simulate curing process (in a real implementation, this would be more complex)
    # For now, we'll just mark it as cured with OK validation
    import time
    time.sleep(1)  # Simulate processing time

    # Update cure status
    dataset_file.cure_status = 'cured'
    dataset_file.cure_validation_status = 'ok'  # or 'warnings', 'errors'
    dataset_file.cured_at = datetime.utcnow()
    db.session.commit()

    # Update dataset statistics
    dataset.updated_at = datetime.utcnow()
    db.session.commit()

    log_user_action(
        "file_cured",
        f"File cured: {dataset_file.show_filename} in dataset '{dataset.name}'",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'File "{dataset_file.show_filename}" cured successfully',
        'file_type': dataset_file.file_type,
        'cure_status': dataset_file.cure_status,
        'validation_status': dataset_file.cure_validation_status
    })

  except Exception as e:
    db.session.rollback()
    # Reset cure status on error
    dataset_file.cure_status = 'not_cured'
    dataset_file.cure_validation_status = 'pending'
    db.session.commit()

    ErrorLogger.log_exception(
        e,
        context=f"Curing file {file_id} from dataset {dataset_id}",
        user_action=f"User trying to cure file from dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_id': file_id,
            'file_type': dataset_file.file_type,
            'filename': dataset_file.show_filename
        }
    )
    log_user_action("file_cure_failed",
                    f"File: {dataset_file.show_filename}", success=False)

    return jsonify({
        'success': False,
        'message': f'Error curing file: {str(e)}'
    }), 500


@files_bp.route('/dataset/<int:dataset_id>/file/<int:file_id>/rename', methods=['POST'])
@login_required
def rename_dataset_file(dataset_id, file_id):
  print("DEBUG: Entered rename_dataset_file")  # Debug log
  """Rename a specific file in a dataset"""
  dataset = Dataset.query.filter_by(
      id=dataset_id, user_id=current_user.id).first_or_404()
  dataset_file = DatasetFile.query.filter_by(
      id=file_id, dataset_id=dataset_id).first_or_404()
  # Debug log
  print(f"DEBUG: Found dataset {dataset.id} and file {dataset_file.id}")
  try:
    # Try to get data as JSON first
    if request.is_json:
      data = request.get_json()
    else:
      # Fallback to form data
      data = request.form

    if not data:
      return jsonify({'success': False, 'message': 'No data received'}), 400

    new_filename = data.get('new_filename', '').strip()

    if not new_filename:
      return jsonify({
          'success': False,
          'message': 'New filename cannot be empty'
      }), 400

    # Validate filename (basic validation)
    if '/' in new_filename or '\\' in new_filename:
      return jsonify({
          'success': False,
          'message': 'Filename cannot contain path separators'
      }), 400

    # Get the original filename for comparison
    old_show_filename = dataset_file.show_filename

    print(f"DEBUG: new_filename = {new_filename}")  # Debug log

    # Check if the new filename already exists in the same dataset
    existing_file = DatasetFile.query.filter_by(
        dataset_id=dataset_id,
        show_filename=new_filename
    ).first()

    if existing_file and existing_file.id != file_id:
      # Generate a unique name with 4-digit number
      base_name = new_filename
      extension = ''
      if '.' in new_filename:
        parts = new_filename.rsplit('.', 1)
        base_name = parts[0]
        extension = '.' + parts[1]

      # Find the next available number
      counter = 1
      while counter < 10000:
        numbered_filename = f"{base_name}_{counter:04d}{extension}"
        existing_numbered = DatasetFile.query.filter_by(
            dataset_id=dataset_id,
            filename=numbered_filename
        ).first()
        if not existing_numbered:
          new_filename = numbered_filename
          break
        counter += 1

      if counter >= 10000:
        return jsonify({
            'success': False,
            'message': 'Could not generate unique filename'
        }), 400

    # Rename the physical file
    old_file_path = dataset_file.file_path
    print(f"DEBUG: old_file_path = {old_file_path}")  # Debug log
    print(f"DEBUG: new_filename = {new_filename}")  # Debug log
    if not old_file_path:
      print("DEBUG: old_file_path is invalid")
      return jsonify({'success': False, 'message': 'File path not found in database'}), 500
    # Debug log
    print(f"DEBUG: Renaming file from {old_file_path} to new {new_filename}")
    # Debug log
    print(f"DEBUG: dataset_file pre= {dataset_file}")
    # Update the database record
    dataset_file.show_filename = new_filename
    dataset_file.modified_at = datetime.utcnow()
    db.session.commit()
    print(f"DEBUG: dataset_file pos= {dataset_file}")

    log_user_action(
        "file_renamed",
        f"File renamed: '{old_show_filename}' → '{new_filename}' in dataset '{dataset.name}'",
        success=True
    )

    return jsonify({
        'success': True,
        'message': f'File renamed to "{new_filename}" successfully',
        'old_filename': old_show_filename,
        'new_filename': new_filename,
        'file_type': dataset_file.file_type
    })

  except Exception as e:
    print(f"DEBUG: Exception in rename_dataset_file: {e}")  # Debug log
    db.session.rollback()
    ErrorLogger.log_exception(
        e,
        context=f"Renaming file {file_id} in dataset {dataset_id}",
        user_action=f"User trying to rename file in dataset '{dataset.name}'",
        extra_data={
            'dataset_id': dataset_id,
            'file_id': file_id,
            'new_filename': data.get('new_filename') if 'data' in locals() else None
        }
    )
    log_user_action("file_rename_failed",
                    f"File ID: {file_id}, New name: {data.get('new_filename') if 'data' in locals() else 'unknown'}",
                    success=False)

    return jsonify({
        'success': False,
        'message': f'Error renaming file: {str(e)}'
    }), 500
