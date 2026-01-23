from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
from .. import Dataset

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/config')
def api_config():
  """API endpoint to get application configuration"""
  user_upload_folder = current_app.config['UPLOAD_FOLDER']
  return jsonify({
      'maxFileSize': current_app.config['MAX_CONTENT_LENGTH'],
      'maxFileSizeMB': current_app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024),
      'allowedFileTypes': ['.csv', '.tsv', '.txt'],
      'uploadFolder': user_upload_folder
  })


@api_bp.route('/api/datasets')
@login_required
def api_datasets():
  """API endpoint to get user's datasets (delegator to archived implementation)"""
  from archive.archived_handlers import api_datasets as _archived_api_datasets
  return _archived_api_datasets()
