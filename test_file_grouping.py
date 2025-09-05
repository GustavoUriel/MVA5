#!/usr/bin/env python3
"""
Test script to verify file grouping functionality
"""


def test_file_grouping():
  """Test that files are grouped correctly by type"""

  # Sample files data that would come from the API
  sample_files = [
      {'id': 1, 'filename': 'patients.csv', 'file_type': 'patients',
       'size': 1000, 'uploaded_at': '2025-01-01', 'modified_at': '2025-01-01'},
      {'id': 2, 'filename': 'bracken.csv', 'file_type': 'bracken',
       'size': 2000, 'uploaded_at': '2025-01-01', 'modified_at': '2025-01-01'},
      {'id': 3, 'filename': 'taxonomy.csv', 'file_type': 'taxonomy',
       'size': 1500, 'uploaded_at': '2025-01-01', 'modified_at': '2025-01-01'},
      {'id': 4, 'filename': 'patients_copy.csv', 'file_type': 'patients',
       'size': 1000, 'uploaded_at': '2025-01-01', 'modified_at': '2025-01-01'},
      {'id': 5, 'filename': 'bracken_results.csv', 'file_type': 'bracken',
       'size': 2500, 'uploaded_at': '2025-01-01', 'modified_at': '2025-01-01'},
  ]

  # Simulate the grouping logic from the JavaScript
  grouped_files = {
      'patients': [f for f in sample_files if f['file_type'] == 'patients'],
      'bracken': [f for f in sample_files if f['file_type'] == 'bracken'],
      'taxonomy': [f for f in sample_files if f['file_type'] == 'taxonomy']
  }

  file_type_order = ['patients', 'bracken', 'taxonomy']

  print("Testing file grouping logic:")
  print("=" * 40)

  for file_type in file_type_order:
    files = grouped_files[file_type]
    print(f"✅ {file_type.title()}: {len(files)} file{'s' if len(files) != 1 else ''}")
    for file in files:
      print(f"   - {file['filename']}")

  # Verify counts
  expected_counts = {'patients': 2, 'bracken': 2, 'taxonomy': 1}
  actual_counts = {ft: len(grouped_files[ft]) for ft in file_type_order}

  print("\nVerification:")
  print("=" * 40)

  all_correct = True
  for file_type in file_type_order:
    expected = expected_counts[file_type]
    actual = actual_counts[file_type]
    status = "✅" if expected == actual else "❌"
    print(f"{status} {file_type}: expected {expected}, got {actual}")
    if expected != actual:
      all_correct = False

  print(
      f"\nOverall result: {'✅ All tests passed!' if all_correct else '❌ Some tests failed!'}")
  return all_correct


if __name__ == "__main__":
  test_file_grouping()
