#!/usr/bin/env python3
"""
Test script to verify the fixed OAuth implementation
"""

import os
import requests
from dotenv import load_dotenv

def test_oauth_endpoints():
    """Test OAuth endpoints directly"""
    print("🔍 Testing OAuth Endpoints...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    print(f"Client ID configured: {'✓' if client_id and client_id != 'dummy-client-id' else '✗'}")
    print(f"Client Secret configured: {'✓' if client_secret and client_secret != 'dummy-client-secret' else '✗'}")
    
    if not client_id or client_id == 'dummy-client-id':
        print("\n❌ GOOGLE_CLIENT_ID not properly configured!")
        return False
    
    # Test token endpoint
    print("\n🌐 Testing Google OAuth Token Endpoint...")
    try:
        token_url = 'https://oauth2.googleapis.com/token'
        # This is just a connectivity test - we can't get a real token without a code
        response = requests.get(token_url, timeout=10)
        print(f"✓ Token endpoint accessible (status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to access token endpoint: {e}")
        return False
    
    # Test userinfo endpoint
    print("\n👤 Testing Google Userinfo Endpoint...")
    try:
        userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        # This will return 401 without a valid token, but that's expected
        response = requests.get(userinfo_url, timeout=10)
        print(f"✓ Userinfo endpoint accessible (status: {response.status_code})")
        if response.status_code == 401:
            print("  (401 is expected without a valid access token)")
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to access userinfo endpoint: {e}")
        return False
    
    print("\n✅ OAuth endpoints test completed!")
    print("\n📋 OAuth Flow Summary:")
    print("1. User visits /auth/login")
    print("2. Redirected to Google OAuth")
    print("3. User authorizes and Google redirects back with 'code'")
    print("4. Application exchanges 'code' for 'access_token'")
    print("5. Application uses 'access_token' to get user info")
    print("6. User is logged in and redirected to dashboard")
    
    return True

def test_application_import():
    """Test that the application imports without OAuth errors"""
    print("\n🔧 Testing Application Import...")
    try:
        import app
        print("✓ Application imports successfully")
        return True
    except Exception as e:
        print(f"✗ Application import failed: {e}")
        return False

if __name__ == '__main__':
    test_oauth_endpoints()
    test_application_import()
