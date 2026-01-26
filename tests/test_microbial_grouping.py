#!/usr/bin/env python3
"""
Simple test for microbial grouping API endpoint
"""

import sys
import os

# Add the app to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'modules'))

try:
    # Import the function directly
    from app.modules.datasets.datasets_bp import get_microbial_grouping_methods

    print("Testing microbial grouping API endpoint...")

    # Test the function directly
    print("\n1. Testing get_microbial_grouping_methods function:")
    try:
        # Call the function - it doesn't need a dataset_id since it just loads metadata
        result = get_microbial_grouping_methods(1)  # Pass dummy dataset_id
        print(f"✓ Function returned result")

        # Check if it's a Flask response object
        if hasattr(result, 'get_json'):
            # It's a Flask response, get the JSON data
            data = result.get_json()
            if data.get('success'):
                methods = data.get('grouping_methods', [])
                print(f"✓ API returned {len(methods)} methods")
                if len(methods) > 0:
                    print(f"  Sample method: {methods[0]['key']} - {methods[0]['name']}")
                    print("✓ Method structure is correct")
                else:
                    print("✗ No methods returned")
            else:
                print("✗ API response success=false")
        else:
            print("✗ Expected Flask response object")

    except Exception as e:
        print(f"✗ Function test failed: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\nTest completed!")

except ImportError as e:
    print(f"Import error: {str(e)}")
    print("Make sure you're in the correct directory and virtual environment is activated")