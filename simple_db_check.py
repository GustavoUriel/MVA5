import sqlite3
import os

# Connect directly to the database
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
print(f"Database path: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check table schema
cursor.execute("PRAGMA table_info(dataset_files)")
columns = cursor.fetchall()
print("Columns in dataset_files:")
for col in columns:
  print(f"  {col[1]} - {col[2]}")

# Check if there are any files
cursor.execute("SELECT COUNT(*) FROM dataset_files")
count = cursor.fetchone()[0]
print(f"\nTotal files: {count}")

if count > 0:
  # Try to select with new columns
  try:
    cursor.execute(
        "SELECT id, cure_status, cure_validation_status FROM dataset_files LIMIT 1")
    row = cursor.fetchone()
    print(f"Sample data: {row}")
  except Exception as e:
    print(f"Error accessing new columns: {e}")

conn.close()
print("Database check completed")
