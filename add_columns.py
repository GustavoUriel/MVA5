import sqlite3
import os

# Connect to the database
db_path = 'instance/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
  # Add the columns
  print("Adding cure_status column...")
  cursor.execute(
      "ALTER TABLE dataset_files ADD COLUMN cure_status VARCHAR(50) DEFAULT 'not_cured'")

  print("Adding cure_validation_status column...")
  cursor.execute(
      "ALTER TABLE dataset_files ADD COLUMN cure_validation_status VARCHAR(50) DEFAULT 'pending'")

  print("Adding cured_at column...")
  cursor.execute("ALTER TABLE dataset_files ADD COLUMN cured_at DATETIME")

  conn.commit()
  print("Migration completed successfully!")

except Exception as e:
  print(f"Error: {e}")
  conn.rollback()

finally:
  conn.close()
