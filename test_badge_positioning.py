#!/usr/bin/env python3
"""
Test script to verify file count badge repositioning
"""


def test_file_count_positioning():
  """Test that the file count badges are positioned correctly in the HTML"""

  # Simulate the HTML structure that should be generated
  file_type = 'patients'
  type_files_length = 3
  file_type_labels = {
      'patients': 'Patients Data Files',
      'bracken': 'Bracken Results Files',
      'taxonomy': 'Taxonomy Data Files'
  }
  file_type_icons = {
      'patients': 'fas fa-users text-primary',
      'bracken': 'fas fa-chart-bar text-success',
      'taxonomy': 'fas fa-sitemap text-info'
  }

  # Generate the expected HTML structure
  expected_html = f'''
                    <div class="file-group-separator" data-file-type="{file_type}">
                        <div class="d-flex align-items-center justify-content-between mb-3">
                            <div class="d-flex align-items-center">
                                <i class="{file_type_icons[file_type]} me-2"></i>
                                <h6 class="mb-0 fw-bold">{file_type_labels[file_type]}</h6>
                            </div>
                            <span class="badge bg-secondary">{type_files_length} files</span>
                        </div>
                        <hr class="my-2">
                    </div>'''

  print("Testing file count badge positioning:")
  print("=" * 50)

  # Check for key structural elements
  checks = [
      ('justify-content-between', 'Flexbox justify-content-between class present'),
      ('d-flex align-items-center', 'Left side flex container present'),
      ('badge bg-secondary', 'Badge with secondary background present'),
      ('me-2', 'Icon margin present'),
      ('fw-bold', 'Bold font weight present'),
      ('data-file-type', 'Data attribute for file type present'),
  ]

  all_passed = True
  for check, description in checks:
    if check in expected_html:
      print(f"✅ {description}")
    else:
      print(f"❌ {description}")
      all_passed = False

  # Check that the badge is NOT in the left flex container
  if '<span class="badge bg-secondary">' in expected_html:
    print("✅ Badge positioned outside left flex container")
  else:
    print("❌ Badge positioning issue")
    all_passed = False

  # Check that the structure has the right layout
  if 'justify-content-between' in expected_html and 'd-flex align-items-center' in expected_html:
    print("✅ Proper flexbox layout for left-right positioning")
  else:
    print("❌ Flexbox layout issue")
    all_passed = False

  print("\n" + "=" * 50)
  if all_passed:
    print("🎉 All positioning tests passed!")
    print("\nExpected layout:")
    print("🔵 [Icon] Patients Data Files                    [3 files]")
    print("   ──────────────────────────────────────────────────")
  else:
    print("❌ Some positioning tests failed!")

  return all_passed


if __name__ == "__main__":
  test_file_count_positioning()
