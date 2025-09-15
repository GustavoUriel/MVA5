"""
Normalize dataset_file paths to the running app's instance path.
This script is safe to run from the repo root and will:
 - back up instance/app.db
 - update dataset_file.file_path and processed_file_path to use app.instance_path as base

Run: py scripts\normalize_paths.py
"""
import sqlite3
import os
import shutil
import time
import json

# Determine repo root as cwd
ROOT = os.getcwd()
DB_PATH = os.path.join(ROOT, 'instance', 'app.db')
if not os.path.exists(DB_PATH):
  print('Database not found at', DB_PATH)
  raise SystemExit(1)

BACKUP = DB_PATH + '.bak_' + str(int(time.time()))
shutil.copy2(DB_PATH, BACKUP)
print('Backup created at', BACKUP)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute(
    'SELECT id, dataset_id, show_filename, file_path, processed_file_path FROM dataset_file')
rows = cur.fetchall()

updated = []
for r in rows:
  id_, dataset_id, show_filename, file_path, processed = r
  if not file_path:
    continue
  # If path already under repo instance, skip
  desired_prefix = os.path.join(ROOT, 'instance')
  if file_path.startswith(desired_prefix.replace('\\', '\\\\')) or file_path.startswith(desired_prefix):
    # likely good
    continue

  # Construct safe email portion: attempt to extract from existing path if possible
  # Fallback: use 'unknown_user' if not possible
  safe_email = None
  parts = file_path.split(os.sep)
  if 'users' in parts:
    try:
      users_idx = parts.index('users')
      safe_email = parts[users_idx+1]
    except Exception:
      safe_email = None
  if not safe_email:
    safe_email = 'unknown_user'

  new_base = os.path.join(desired_prefix, 'users',
                          safe_email, str(dataset_id), 'files')
  os.makedirs(new_base, exist_ok=True)

  new_file_path = os.path.join(new_base, os.path.basename(file_path))
  print(f"Updating id={id_} from {file_path} → {new_file_path}")
  cur.execute('UPDATE dataset_file SET file_path = ? WHERE id = ?',
              (new_file_path, id_))
  if processed:
    new_processed = os.path.join(new_base, os.path.basename(processed))
    print(f"Updating processed for id={id_} from {processed} → {new_processed}")
    cur.execute(
        'UPDATE dataset_file SET processed_file_path = ? WHERE id = ?', (new_processed, id_))
  updated.append(id_)

conn.commit()
conn.close()
print('Updated rows:', updated)
print('Done')
