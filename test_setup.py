"""
Quick test script to verify the application setup
"""

import os
import sys
from flask import Flask


def test_imports():
  """Test that all modules can be imported"""
  try:
    print("Testing imports...")

    # Test core modules
    import app
    print("✓ app module imported")

    import config
    print("✓ config module imported")

    import extensions
    print("✓ extensions module imported")

    import models
    print("✓ models module imported")

    # Test blueprint modules
    from auth import routes as auth_routes
    print("✓ auth routes imported")

    from datasets import routes as dataset_routes
    print("✓ dataset routes imported")

    # Test utility modules
    from utils import logging_config, file_utils
    print("✓ utils modules imported")

    # Test tasks
    from tasks import analysis_tasks
    print("✓ task modules imported")

    print("\n✅ All imports successful!")
    return True

  except ImportError as e:
    print(f"\n❌ Import error: {e}")
    return False


def test_app_creation():
  """Test app creation"""
  try:
    print("\nTesting app creation...")
    from app import create_app

    app = create_app()
    print("✓ Flask app created successfully")

    with app.app_context():
      from extensions import db
      print("✓ Database context available")

    print("\n✅ App creation successful!")
    return True

  except Exception as e:
    print(f"\n❌ App creation error: {e}")
    return False


def check_environment():
  """Check environment setup"""
  print("\nChecking environment...")

  # Check for .env file
  if os.path.exists('.env'):
    print("✓ .env file found")
  else:
    print("⚠️  .env file not found (you can copy from .env.example)")

  # Check required directories
  for directory in ['uploads', 'logs']:
    if os.path.exists(directory):
      print(f"✓ {directory} directory exists")
    else:
      print(f"⚠️  {directory} directory missing (will be created automatically)")

  # Check for Redis (optional)
  try:
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print("✓ Redis server is running")
  except:
    print("⚠️  Redis server not available (needed for Celery)")

  return True


if __name__ == "__main__":
  print("🧪 Microbiome Analysis App - Setup Test\n")
  print("=" * 50)

  success = True

  # Run tests
  success &= check_environment()
  success &= test_imports()
  success &= test_app_creation()

  print("\n" + "=" * 50)

  if success:
    print("🎉 All tests passed! Your application is ready to run.")
    print("\nNext steps:")
    print("1. Set up Google OAuth credentials in .env file")
    print("2. Start Redis server: redis-server")
    print("3. Start Celery worker: celery -A celery_worker.celery_app worker --loglevel=info")
    print("4. Run the app: python app.py")
  else:
    print("❌ Some tests failed. Please check the errors above.")
    sys.exit(1)
