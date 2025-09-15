"""
File utility functions for the Flask application
"""
import os
try:
  # Import current_app if running inside Flask application context
  from flask import current_app
except Exception:
  current_app = None


def get_dataset_files_folder(user_email, dataset_id):
  """Get the files folder path for a specific dataset.

  Prefer using Flask's instance path when available so uploads and
  lookups are colocated under the same directory. Falls back to the
  repository working directory's `instance` folder when not running
  inside an application context.
  """
  if not user_email or not dataset_id:
    return None

  # Create safe folder name from email (replace special chars)
  safe_email = user_email.replace(
      '@', '_at_').replace('.', '_dot_').replace('-', '_')

  base_instance = None
  if current_app:
    try:
      base_instance = current_app.instance_path
    except Exception:
      base_instance = None

  if not base_instance:
    base_instance = os.path.join(os.getcwd(), 'instance')

  dataset_dir = os.path.join(base_instance, 'users',
                             safe_email, str(dataset_id))
  files_dir = os.path.join(dataset_dir, 'files')
  os.makedirs(files_dir, exist_ok=True)
  return files_dir
