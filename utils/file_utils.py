"""
File Utilities
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
  """Check if file extension is allowed"""
  allowed_extensions = current_app.config.get(
      'ALLOWED_EXTENSIONS', {'csv', 'txt', 'tsv', 'xlsx', 'json'})
  return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, user_id, dataset_uuid):
  """Save uploaded file and return file path and size"""
  if not file or not allowed_file(file.filename):
    raise ValueError("Invalid file")

  # Create upload directory structure
  upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
  user_folder = os.path.join(upload_folder, str(user_id))
  dataset_folder = os.path.join(user_folder, dataset_uuid)

  os.makedirs(dataset_folder, exist_ok=True)

  # Generate secure filename
  filename = secure_filename(file.filename)
  if not filename:
    filename = f"upload_{uuid.uuid4().hex}.txt"

  # Add UUID to filename to ensure uniqueness
  name, ext = os.path.splitext(filename)
  unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"

  file_path = os.path.join(dataset_folder, unique_filename)

  # Save file
  file.save(file_path)

  # Get file size
  file_size = os.path.getsize(file_path)

  return file_path, file_size


def delete_file_safely(file_path):
  """Safely delete a file"""
  try:
    if file_path and os.path.exists(file_path):
      os.remove(file_path)
      return True
  except Exception as e:
    current_app.logger.error(f"Error deleting file {file_path}: {str(e)}")
  return False


def get_file_info(file_path):
  """Get file information"""
  if not file_path or not os.path.exists(file_path):
    return None

  stat = os.stat(file_path)
  return {
      'size': stat.st_size,
      'created': stat.st_ctime,
      'modified': stat.st_mtime,
      'exists': True
  }
