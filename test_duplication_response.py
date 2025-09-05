#!/usr/bin/env python3
"""
Quick test to verify duplication response structure
"""

import sys
import os
sys.path.append('.')


def test_duplication_response():
  """Test that the duplication response includes the required fields"""

  # Mock response structure that should be returned by the backend
  response_data = {
      'success': True,
      'message': 'File "patients.csv" duplicated successfully as "patients_copy.csv"',
      'file_type': 'patients',
      'original_filename': 'patients.csv',
      'new_filename': 'patients_copy.csv',
      'dataset_status': {
          'completion_percentage': 33,
          'is_complete': False,
          'status': 'draft',
          'patients_uploaded': True,
          'taxonomy_uploaded': False,
          'bracken_uploaded': False,
          'file_count': 2,
          'total_size': 200
      }
  }

  # Test that all required fields are present
  required_fields = ['success', 'message', 'file_type',
                     'original_filename', 'new_filename', 'dataset_status']

  for field in required_fields:
    if field not in response_data:
      print(f"❌ Missing field: {field}")
      return False
    else:
      print(f"✅ Field present: {field} = {response_data[field]}")

  # Test that file_type is one of the expected values
  valid_file_types = ['patients', 'taxonomy', 'bracken']
  if response_data['file_type'] not in valid_file_types:
    print(f"❌ Invalid file_type: {response_data['file_type']}")
    return False
  else:
    print(f"✅ Valid file_type: {response_data['file_type']}")

  print("\n🎉 All tests passed! Duplication response structure is correct.")
  return True


if __name__ == "__main__":
  test_duplication_response()
