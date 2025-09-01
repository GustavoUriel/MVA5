#!/usr/bin/env python3
"""
Test script to verify OAuth configuration
"""

import os
import requests
from dotenv import load_dotenv

def test_oauth_configuration():
    """Test OAuth configuration and metadata endpoints"""
    print("🔍 Testing OAuth Configuration...")
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
        print("Please set up your Google OAuth credentials:")
        print("1. Go to https://console.developers.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Google+ API")
        print("4. Create OAuth 2.0 credentials")
        print("5. Add your redirect URI: http://127.0.0.1:5005/auth/login/authorized")
        print("6. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables")
        return False
    
    # Test Google's OpenID Connect discovery endpoint
    print("\n🌐 Testing Google OpenID Connect Discovery...")
    try:
        discovery_url = 'https://accounts.google.com/.well-known/openid_configuration'
        response = requests.get(discovery_url, timeout=10)
        
        if response.status_code == 200:
            metadata = response.json()
            print("✓ OpenID Connect discovery endpoint accessible")
            print(f"✓ Authorization endpoint: {metadata.get('authorization_endpoint', 'N/A')}")
            print(f"✓ Token endpoint: {metadata.get('token_endpoint', 'N/A')}")
            print(f"✓ JWKS URI: {metadata.get('jwks_uri', 'N/A')}")
            print(f"✓ Userinfo endpoint: {metadata.get('userinfo_endpoint', 'N/A')}")
            
            # Check for required endpoints
            required_endpoints = ['authorization_endpoint', 'token_endpoint', 'jwks_uri', 'userinfo_endpoint']
            missing_endpoints = [ep for ep in required_endpoints if ep not in metadata]
            
            if missing_endpoints:
                print(f"⚠️  Missing endpoints: {missing_endpoints}")
            else:
                print("✓ All required endpoints present")
                
        else:
            print(f"✗ Discovery endpoint returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to access discovery endpoint: {e}")
        return False
    
    # Test JWKS endpoint
    print("\n🔑 Testing JWKS (JSON Web Key Set) endpoint...")
    try:
        jwks_url = 'https://www.googleapis.com/oauth2/v3/certs'
        response = requests.get(jwks_url, timeout=10)
        
        if response.status_code == 200:
            jwks = response.json()
            if 'keys' in jwks and len(jwks['keys']) > 0:
                print(f"✓ JWKS endpoint accessible with {len(jwks['keys'])} keys")
            else:
                print("⚠️  JWKS endpoint accessible but no keys found")
        else:
            print(f"✗ JWKS endpoint returned status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to access JWKS endpoint: {e}")
    
    print("\n✅ OAuth configuration test completed!")
    print("\n📋 Next steps:")
    print("1. Ensure your redirect URI is configured in Google Console")
    print("2. Test the login flow in your application")
    print("3. Check logs for any remaining issues")
    
    return True

def create_env_template():
    """Create a template .env file with OAuth configuration"""
    template = """# Google OAuth Configuration
# Get these from https://console.developers.google.com/
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://127.0.0.1:5005/auth/login/authorized

# Flask Configuration
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///microbiome_analysis.db

# Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
"""
    
    with open('.env.template', 'w') as f:
        f.write(template)
    print("\n📄 Created .env.template file with OAuth configuration")

if __name__ == '__main__':
    test_oauth_configuration()
    create_env_template()
