#!/usr/bin/env python3
import sqlite3
import os


def check_database():
  db_path = 'instance/app.db'
  if not os.path.exists(db_path):
    print(f"Database file not found: {db_path}")
    return

  print(f"Checking database: {db_path}")

  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  try:
    # Check table schema
    cursor.execute("PRAGMA table_info(dataset_files)")
    columns = cursor.fetchall()
    print(f"\nFound {len(columns)} columns in dataset_files:")
    for col in columns:
      print(f"  {col[1]} ({col[2]})")

    # Check for new columns
    column_names = [col[1] for col in columns]
    new_columns = ['cure_status', 'cure_validation_status', 'cured_at']
    missing_columns = [col for col in new_columns if col not in column_names]

    if missing_columns:
      print(f"\n❌ Missing columns: {missing_columns}")
      print("The migration did not complete successfully.")
    else:
      print("\n✅ All cure status columns are present!")

    # Check file count
    cursor.execute("SELECT COUNT(*) FROM dataset_files")
    count = cursor.fetchone()[0]
    print(f"\nTotal files in database: {count}")

  except Exception as e:
    print(f"Error checking database: {e}")
  finally:
    conn.close()


if __name__ == "__main__":
  check_database()
