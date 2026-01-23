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


@files_bp.route('/dataset/<int:dataset_id>/file/<int:file_id>/cure', methods=['POST'])
@login_required
def cure_dataset_file(dataset_id, file_id):
  """Cure (process and validate) a specific file in a dataset"""
  from archive.archived_handlers import cure_dataset_file as _archived_cure_dataset_file
  return _archived_cure_dataset_file(dataset_id, file_id)


@files_bp.route('/dataset/<int:dataset_id>/file/<int:file_id>/rename', methods=['POST'])
@login_required
def rename_dataset_file(dataset_id, file_id):
  """Rename a specific file in a dataset"""
  from archive.archived_handlers import rename_dataset_file as _archived_rename_dataset_file
  return _archived_rename_dataset_file(dataset_id, file_id)
