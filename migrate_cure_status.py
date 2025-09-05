"""
Migration script to add cure status fields to DatasetFile model
Run this script once to add the new columns to the database
"""

import sqlite3
import os


def run_migration():
  """Add cure status columns to dataset_files table"""

  db_path = 'instance/app.db'
  if not os.path.exists(db_path):
    print(f"Database file not found: {db_path}")
    return False

  print(f"Connecting to database: {db_path}")
  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  try:
    # Check existing columns
    cursor.execute("PRAGMA table_info(dataset_files)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    print(f"Existing columns: {existing_columns}")

    # Add cure_status column if it doesn't exist
    if 'cure_status' not in existing_columns:
      print("Adding cure_status column...")
      cursor.execute(
          "ALTER TABLE dataset_files ADD COLUMN cure_status VARCHAR(50) DEFAULT 'not_cured'")
      print("✓ cure_status column added")
    else:
      print("✓ cure_status column already exists")

    # Add cure_validation_status column if it doesn't exist
    if 'cure_validation_status' not in existing_columns:
      print("Adding cure_validation_status column...")
      cursor.execute(
          "ALTER TABLE dataset_files ADD COLUMN cure_validation_status VARCHAR(50) DEFAULT 'pending'")
      print("✓ cure_validation_status column added")
    else:
      print("✓ cure_validation_status column already exists")

    # Add cured_at column if it doesn't exist
    if 'cured_at' not in existing_columns:
      print("Adding cured_at column...")
      cursor.execute("ALTER TABLE dataset_files ADD COLUMN cured_at DATETIME")
      print("✓ cured_at column added")
    else:
      print("✓ cured_at column already exists")

    conn.commit()
    print("\nMigration completed successfully!")

    # Verify the changes
    cursor.execute("PRAGMA table_info(dataset_files)")
    final_columns = [row[1] for row in cursor.fetchall()]
    print(f"Final columns: {final_columns}")

  except Exception as e:
    print(f"Error during migration: {e}")
    conn.rollback()
    return False
  finally:
    conn.close()

  return True


if __name__ == "__main__":
  print("Starting database migration for cure status fields...")
  success = run_migration()
  if success:
    print("\n✅ Migration completed successfully!")
  else:
    print("\n❌ Migration failed!")
    exit(1)
