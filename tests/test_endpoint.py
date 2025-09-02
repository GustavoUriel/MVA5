#!/usr/bin/env python3
"""
Simple test script to test the API endpoint
"""

import requests
import json

def test_endpoint():
    """Test the API endpoint"""
    base_url = "http://127.0.0.1:5005"
    endpoint = "/api/dataset/1/table/patients"
    
    print(f"Testing endpoint: {base_url}{endpoint}")
    print("=" * 50)
    
    try:
        # Test without authentication (should return 401)
        print("1. Testing without authentication...")
        response = requests.get(f"{base_url}{endpoint}")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        print()
        
        # Test with a dummy session cookie
        print("2. Testing with dummy session cookie...")
        headers = {'Cookie': 'session=dummy_session'}
        response = requests.get(f"{base_url}{endpoint}", headers=headers)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        print()
        
        # Test with a different endpoint to see if the server is running
        print("3. Testing if server is running...")
        response = requests.get(f"{base_url}/")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response length: {len(response.text)}")
        print()
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("   Make sure the Flask app is running on http://127.0.0.1:5005")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoint()

