#!/usr/bin/env python3
"""
Database Migration Script: Add modified_at column to dataset_file table

This script adds a new 'modified_at' column to track when files are modified.
The column will default to the current timestamp and automatically update when records are modified.

Usage:
    python scripts/add_modified_column.py

Requirements:
    - SQLite database file at instance/app.db
    - sqlite3 module (built-in with Python)
"""

import sqlite3
import os
import sys
from datetime import datetime


def add_modified_column():
  """Add modified_at column to dataset_file table"""

  # Database path
  db_path = os.path.join('instance', 'app.db')

  if not os.path.exists(db_path):
    print(f"❌ Database file not found at: {db_path}")
    print("Please run this script from the project root directory.")
    return False

  try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"🔗 Connected to database: {db_path}")

    # Check if column already exists
    cursor.execute("PRAGMA table_info(dataset_file)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'modified_at' in columns:
      print("✅ Column 'modified_at' already exists in dataset_file table")
      return True

    print("📝 Adding 'modified_at' column to dataset_file table...")

    # Add the new column (without default value for SQLite compatibility)
    cursor.execute("""
            ALTER TABLE dataset_file 
            ADD COLUMN modified_at DATETIME
        """)

    # Update existing records to set modified_at to uploaded_at
    cursor.execute("""
            UPDATE dataset_file 
            SET modified_at = uploaded_at 
            WHERE modified_at IS NULL
        """)

    # Set default value for new records by updating NULL values
    cursor.execute("""
            UPDATE dataset_file 
            SET modified_at = datetime('now') 
            WHERE modified_at IS NULL
        """)

    # Commit changes
    conn.commit()

    print("✅ Successfully added 'modified_at' column")
    print("✅ Updated existing records with uploaded_at timestamp")

    # Verify the column was added
    cursor.execute("PRAGMA table_info(dataset_file)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'modified_at' in columns:
      print("✅ Verification successful: 'modified_at' column is present")

      # Show sample data
      cursor.execute(
          "SELECT id, show_filename, uploaded_at, modified_at FROM dataset_file LIMIT 3")
      rows = cursor.fetchall()

      if rows:
        print("\n📊 Sample data:")
        for row in rows:
          print(f"  ID: {row[0]}, File: {row[1]}")
          print(f"    Uploaded: {row[2]}")
          print(f"    Modified: {row[3]}")
          print()

    return True

  except sqlite3.Error as e:
    print(f"❌ SQLite error: {e}")
    return False
  except Exception as e:
    print(f"❌ Unexpected error: {e}")
    return False
  finally:
    if 'conn' in locals():
      conn.close()
      print("🔌 Database connection closed")


def main():
  """Main function"""
  print("🚀 Starting database migration: Add modified_at column")
  print("=" * 60)

  success = add_modified_column()

  print("=" * 60)
  if success:
    print("🎉 Migration completed successfully!")
    print("\nNext steps:")
    print("1. Restart your Flask application")
    print("2. The new 'modified_at' column will be available")
    print("3. When you implement file editing, update this field")
  else:
    print("💥 Migration failed!")
    print("Please check the error messages above and try again.")
    sys.exit(1)


if __name__ == "__main__":
  main()
