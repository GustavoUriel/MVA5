import sqlite3
import os

# Direct database access
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
print(f"Database path: {db_path}")

if os.path.exists(db_path):
  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  # Check tables
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
  tables = cursor.fetchall()
  print("Tables:", tables)

  # Check datasets
  try:
    cursor.execute("SELECT id, name, user_id, status FROM dataset")
    datasets = cursor.fetchall()
    print(f"Datasets ({len(datasets)}):")
    for d in datasets:
      print(f"  ID: {d[0]}, Name: {d[1]}, User: {d[2]}, Status: {d[3]}")
  except sqlite3.OperationalError as e:
    print(f"Error querying dataset table: {e}")

  # Check users
  try:
    cursor.execute("SELECT id, email FROM user")
    users = cursor.fetchall()
    print(f"Users ({len(users)}):")
    for u in users:
      print(f"  ID: {u[0]}, Email: {u[1]}")
  except sqlite3.OperationalError as e:
    print(f"Error querying user table: {e}")

  conn.close()
else:
  print("Database file not found")
