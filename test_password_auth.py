#!/usr/bin/env python3
"""
Test script for password authentication feature.
This script demonstrates how the password authentication works with different scenarios.
"""

import requests
import json
import sys
import os

def test_password_authentication():
    """Test the password authentication feature with different scenarios."""
    
    base_url = "http://localhost:5000"
    
    print("🔐 Testing Password Authentication Feature")
    print("=" * 50)
    
    # Test 1: Valid password in Authorization header (should succeed)
    print("\n1. Testing valid password in Authorization header (should succeed):")
    try:
        headers = {
            'Content-Type': 'text/plain',
            'Authorization': 'test_password'
        }
        response = requests.post(f"{base_url}/update-dns", data="127.0.0.1", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running. Start the service first.")
        return
    
    # Test 2: Valid password in Bearer format (should succeed)
    print("\n2. Testing valid password in Bearer format (should succeed):")
    try:
        headers = {
            'Content-Type': 'text/plain',
            'Authorization': 'Bearer test_password'
        }
        response = requests.post(f"{base_url}/update-dns", data="127.0.0.1", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 3: Valid password in custom header (should succeed)
    print("\n3. Testing valid password in X-Auth-Password header (should succeed):")
    try:
        headers = {
            'Content-Type': 'text/plain',
            'X-Auth-Password': 'test_password'
        }
        response = requests.post(f"{base_url}/update-dns", data="127.0.0.1", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 4: Valid password in query parameter (should succeed)
    print("\n4. Testing valid password in query parameter (should succeed):")
    try:
        response = requests.post(f"{base_url}/update-dns?password=test_password", data="127.0.0.1")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 5: Invalid password (should fail with 401)
    print("\n5. Testing invalid password (should fail with 401):")
    try:
        headers = {
            'Content-Type': 'text/plain',
            'Authorization': 'wrong_password'
        }
        response = requests.post(f"{base_url}/update-dns", data="127.0.0.1", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 6: No password (should fail with 401)
    print("\n6. Testing no password (should fail with 401):")
    try:
        response = requests.post(f"{base_url}/update-dns", data="127.0.0.1")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 7: Health check (should succeed without authentication)
    print("\n7. Testing health check (should succeed without authentication):")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    print("\n" + "=" * 50)
    print("📋 Password Authentication Configuration Options:")
    print()
    print("To enable password authentication:")
    print("export ENABLE_PASSWORD_AUTH=true")
    print("export AUTH_PASSWORD=your_secure_password")
    print()
    print("To disable password authentication:")
    print("export ENABLE_PASSWORD_AUTH=false")
    print()
    print("Supported authentication methods:")
    print("1. Authorization header: -H 'Authorization: your_password'")
    print("2. Bearer token: -H 'Authorization: Bearer your_password'")
    print("3. Custom header: -H 'X-Auth-Password: your_password'")
    print("4. Query parameter: ?password=your_password")
    print()
    print("For more information, see the README.md file.")

if __name__ == "__main__":
    test_password_authentication() 