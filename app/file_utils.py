"""
File utility functions for the Flask application
"""
import os


def get_dataset_files_folder(user_email, dataset_id):
  """Get the files folder path for a specific dataset"""
  if user_email and dataset_id:
    # Create safe folder name from email (replace special chars)
    safe_email = user_email.replace(
        '@', '_at_').replace('.', '_dot_').replace('-', '_')
    dataset_dir = os.path.join(
        os.getcwd(), 'instance', 'users', safe_email, str(dataset_id))
    files_dir = os.path.join(dataset_dir, 'files')
    os.makedirs(files_dir, exist_ok=True)
    return files_dir
  return None
