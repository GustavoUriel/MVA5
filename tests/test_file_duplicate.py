"""
Test cases for the file duplicate functionality
"""

import flask_login
from flask_login import current_user
import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from app import app, db, Dataset, DatasetFile, User
from datetime import datetime

# Create a mock user for testing


class MockUser:
  def __init__(self, user_id):
    self.id = user_id
    self.is_authenticated = True


# Patch the current_user for testing


class TestFileDuplicateAPI(unittest.TestCase):
  """Test cases for the file duplicate API endpoint"""

  def setUp(self):
    """Set up test environment"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'

    self.app = app.test_client()
    self.app_context = app.app_context()
    self.app_context.push()

    # Create database tables
    db.create_all()

    # Create test user
    self.test_user = User(
        email='test@example.com',
        name='Test User',
        google_id='test_google_id'
    )
    db.session.add(self.test_user)
    db.session.commit()

    # Create test dataset
    self.test_dataset = Dataset(
        name='Test Dataset',
        description='Test dataset for duplicate functionality',
        user_id=self.test_user.id
    )
    db.session.add(self.test_dataset)
    db.session.commit()

    # Create a temporary directory for test files
    self.temp_dir = tempfile.mkdtemp()

    # Mock the get_user_upload_folder function
    with patch('app.get_user_upload_folder', return_value=self.temp_dir):
      # Create a test file
      self.test_file_path = os.path.join(self.temp_dir, 'test_patients.csv')
      with open(self.test_file_path, 'w') as f:
        f.write('patient_id,value\n1,10\n2,20\n')

      # Create test dataset file
      self.test_file = DatasetFile(
          dataset_id=self.test_dataset.id,
          file_type='patients',
          filename='test_patients.csv',
          original_filename='patients.csv',
          file_size=os.path.getsize(self.test_file_path),
          upload_method='file'
      )
      db.session.add(self.test_file)
      db.session.commit()

  def tearDown(self):
    """Clean up test environment"""
    self.app_context.pop()
    # Clean up temporary files
    if os.path.exists(self.temp_dir):
      shutil.rmtree(self.temp_dir)

  @patch('flask_login.current_user')
  def test_duplicate_file_success(self, mock_current_user):
    """Test successful file duplication"""
    mock_current_user.id = self.test_user.id
    mock_current_user.is_authenticated = True

    with patch('app.get_user_upload_folder', return_value=self.temp_dir):
      # Make the duplicate request
      response = self.app.post(
          f'/dataset/{self.test_dataset.id}/file/{self.test_file.id}/duplicate',
          content_type='application/json'
      )

      # Check response
      self.assertEqual(response.status_code, 200)
      data = json.loads(response.data)
      self.assertTrue(data['success'])
      self.assertIn('duplicated successfully', data['message'])

      # Check that a new file was created in the database
      files = DatasetFile.query.filter_by(dataset_id=self.test_dataset.id).all()
      self.assertEqual(len(files), 2)

      # Check that the new file has the correct name
      new_file = [f for f in files if f.id != self.test_file.id][0]
      self.assertEqual(new_file.original_filename, 'patients_copy.csv')
      self.assertTrue(new_file.filename.endswith('_copy.csv'))

      # Check that the physical file was copied
      new_file_path = os.path.join(self.temp_dir, new_file.filename)
      self.assertTrue(os.path.exists(new_file_path))

  @patch('flask_login.current_user')
  def test_duplicate_file_not_found(self, mock_current_user):
    """Test duplicating a non-existent file"""
    mock_current_user.id = self.test_user.id
    mock_current_user.is_authenticated = True

    # Try to duplicate a file that doesn't exist
    response = self.app.post(
        f'/dataset/{self.test_dataset.id}/file/99999/duplicate',
        content_type='application/json'
    )

    # Should return 404
    self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
  unittest.main()
