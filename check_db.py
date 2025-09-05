from sqlalchemy import text
from app import app, db
print("Starting database check...")


print("App imported, creating context...")
app.app_context().push()
print("App context created")

try:
  print("Connecting to database...")
  with db.engine.connect() as conn:
    print("Executing PRAGMA query...")
    result = conn.execute(text('PRAGMA table_info(dataset_files)'))
    columns = [row[1] for row in result.fetchall()]
    print('Columns in dataset_files:', columns)

    # Also check if there are any files
    print("Checking file count...")
    result = conn.execute(text('SELECT COUNT(*) FROM dataset_files'))
    count = result.fetchone()[0]
    print(f'Total files in database: {count}')

    # Try to select one file with the new columns
    if count > 0:
      print("Testing new columns...")
      result = conn.execute(
          text('SELECT id, cure_status, cure_validation_status FROM dataset_files LIMIT 1'))
      row = result.fetchone()
      print(f'Sample file data: {row}')

except Exception as e:
  print(f"Error: {e}")
  import traceback
  traceback.print_exc()

print("Database check completed")
