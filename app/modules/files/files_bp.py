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
  from archive.archived_handlers import delete_dataset_file as _archived_delete_dataset_file
  return _archived_delete_dataset_file(dataset_id, file_id)


@files_bp.route('/dataset/<int:dataset_id>/file/<int:file_id>/duplicate', methods=['POST'])
@login_required
def duplicate_dataset_file(dataset_id, file_id):
  """Duplicate a specific file in a dataset"""
  from archive.archived_handlers import duplicate_dataset_file as _archived_duplicate_dataset_file
  return _archived_duplicate_dataset_file(dataset_id, file_id)


@files_bp.route('/dataset/<int:dataset_id>/file/<int:file_id>/curate', methods=['POST'])
@login_required
def curate_dataset_file(dataset_id, file_id):
  """Curate (curate) a specific file in a dataset by calling the dataCuration.curate
  method with the file path, and mark the file as curated so it won't be
  curated again."""
  from app.modules.dataCuration.dataCuration import curate

  dataset = Dataset.query.get(dataset_id)
  if not dataset:
    return jsonify({'success': False, 'error': 'Dataset not found'}), 404

  dfile = DatasetFile.query.filter_by(id=file_id, dataset_id=dataset_id).first()
  if not dfile:
    return jsonify({'success': False, 'error': 'File not found'}), 404

  # If already curated, skip
  if getattr(dfile, 'curated', 'not_cured') == 'curated':
    return jsonify({'success': True, 'message': 'File already curated'}), 200

  # determine file path attribute
  file_path = getattr(dfile, 'path', None) or getattr(dfile, 'filepath', None) or getattr(dfile, 'file_path', None)
  if not file_path:
    return jsonify({'success': False, 'error': 'File path not available'}), 400

  try:
    # call the curate function with the file path
    curate(file_path)

    # mark the file as curated (handle common attribute names)
    if hasattr(dfile, 'curated'):
      dfile.curated = 'curated'
      dfile.curated_validation_status = 'ok'
    elif hasattr(dfile, 'is_curated'):
      dfile.is_curated = True
    else:
      setattr(dfile, 'curated', 'curated')

    db.session.add(dfile)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Data curation completed successfully'}), 200
  except Exception as e:
    current_app.logger.exception('Error during curation')
    db.session.rollback()
    return jsonify({'success': False, 'error': 'curation_failed', 'message': str(e)}), 500


@files_bp.route('/dataset/<int:dataset_id>/file/<int:file_id>/rename', methods=['POST'])
@login_required
def rename_dataset_file(dataset_id, file_id):
  """Rename a specific file in a dataset"""
  from archive.archived_handlers import rename_dataset_file as _archived_rename_dataset_file
  return _archived_rename_dataset_file(dataset_id, file_id)
