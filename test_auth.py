#!/usr/bin/env python3
"""
Test script for authentication functionality.
This script tests the new authentication system for logs and stats pages.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_PASSWORD = "test_password"

def test_authentication():
    """Test the authentication functionality."""
    print("🔐 Testing Authentication System")
    print("=" * 50)
    
    # Test 1: Access logs without authentication (should redirect to login)
    print("\n1. Testing access to logs without authentication:")
    try:
        response = requests.get(f"{BASE_URL}/logs", allow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        else:
            print("   ❌ Should require authentication")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running. Start the service first.")
        return
    
    # Test 2: Access API without authentication (should return 401)
    print("\n2. Testing access to API without authentication:")
    try:
        response = requests.get(f"{BASE_URL}/api/logs")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        else:
            print("   ❌ Should require authentication")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 3: Login with valid password
    print("\n3. Testing login with valid password:")
    try:
        response = requests.post(f"{BASE_URL}/login", data={'password': TEST_PASSWORD})
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:  # Redirect to logs
            print("   ✅ Login successful")
            # Get cookies for next tests
            cookies = response.cookies
        else:
            print("   ❌ Login failed")
            cookies = None
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 4: Access logs with valid authentication
    if cookies:
        print("\n4. Testing access to logs with valid authentication:")
        try:
            response = requests.get(f"{BASE_URL}/logs", cookies=cookies)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Successfully accessed logs")
            else:
                print("   ❌ Failed to access logs")
        except requests.exceptions.ConnectionError:
            print("   ❌ Service not running.")
            return
    
    # Test 5: Access API with valid authentication
    if cookies:
        print("\n5. Testing access to API with valid authentication:")
        try:
            response = requests.get(f"{BASE_URL}/api/logs", cookies=cookies)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("   ✅ Successfully accessed API")
                else:
                    print("   ❌ API returned error")
            else:
                print("   ❌ Failed to access API")
        except requests.exceptions.ConnectionError:
            print("   ❌ Service not running.")
            return
    
    # Test 6: Access API with password parameter
    print("\n6. Testing access to API with password parameter:")
    try:
        response = requests.get(f"{BASE_URL}/api/logs?password={TEST_PASSWORD}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Successfully accessed API with password parameter")
        else:
            print("   ❌ Failed to access API with password parameter")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 7: Logout functionality
    if cookies:
        print("\n7. Testing logout functionality:")
        try:
            response = requests.post(f"{BASE_URL}/logout", cookies=cookies)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Logout successful")
            else:
                print("   ❌ Logout failed")
        except requests.exceptions.ConnectionError:
            print("   ❌ Service not running.")
            return
    
    # Test 8: Access after logout (should fail)
    print("\n8. Testing access after logout:")
    try:
        response = requests.get(f"{BASE_URL}/logs", cookies=cookies)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly denied access after logout")
        else:
            print("   ❌ Should deny access after logout")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    print("\n" + "=" * 50)
    print("📋 Authentication Features:")
    print()
    print("✅ Features implemented:")
    print("   - Automatic access from last successful DNS update IP")
    print("   - Password-based authentication")
    print("   - Cookie-based session management")
    print("   - API access with password parameter")
    print("   - Secure logout functionality")
    print()
    print("🔧 Configuration:")
    print("   - Set ENABLE_PASSWORD_AUTH=true to enable authentication")
    print("   - Set AUTH_PASSWORD=your_password for access")
    print("   - Set FLASK_SECRET_KEY for secure cookie management")
    print()
    print("💡 Usage:")
    print("   - Visit /login to access logs and stats")
    print("   - Use same password as DNS update service")
    print("   - Login remembered for 24 hours")
    print("   - API access: /api/logs?password=your_password")

if __name__ == "__main__":
    test_authentication() 