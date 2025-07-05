#!/usr/bin/env python3
"""
Test script for RouterOS format compatibility.
This script demonstrates how the service handles RouterOS-style requests.
"""

import requests
import json
import sys
import os

def test_routeros_format():
    """Test the RouterOS format compatibility."""
    
    base_url = "http://localhost:5000"
    
    print("🔄 Testing RouterOS Format Compatibility")
    print("=" * 50)
    
    # Test 1: RouterOS format with valid password (should succeed)
    print("\n1. Testing RouterOS format with valid password (should succeed):")
    try:
        routeros_data = "127.0.0.1 test_password"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(f"{base_url}/update-dns", data=routeros_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running. Start the service first.")
        return
    
    # Test 2: RouterOS format with invalid password (should fail with 401)
    print("\n2. Testing RouterOS format with invalid password (should fail with 401):")
    try:
        routeros_data = "127.0.0.1 wrong_password"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(f"{base_url}/update-dns", data=routeros_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 3: RouterOS format with invalid IP (should fail with 400)
    print("\n3. Testing RouterOS format with invalid IP (should fail with 400):")
    try:
        routeros_data = "invalid_ip test_password"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(f"{base_url}/update-dns", data=routeros_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 4: RouterOS format with too many parts (should fail with 400)
    print("\n4. Testing RouterOS format with too many parts (should fail with 400):")
    try:
        routeros_data = "127.0.0.1 test_password extra_part"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(f"{base_url}/update-dns", data=routeros_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 5: Plain IP format (backward compatibility)
    print("\n5. Testing plain IP format (backward compatibility):")
    try:
        headers = {
            'Content-Type': 'text/plain',
            'Authorization': 'test_password'
        }
        response = requests.post(f"{base_url}/update-dns", data="127.0.0.1", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 6: Empty data (should fail with 400)
    print("\n6. Testing empty data (should fail with 400):")
    try:
        response = requests.post(f"{base_url}/update-dns", data="")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    print("\n" + "=" * 50)
    print("📋 RouterOS Format Features:")
    print()
    print("✅ Supported formats:")
    print("   - RouterOS: 'IP PASSWORD'")
    print("   - Plain IP: 'IP' (with headers)")
    print()
    print("🔧 RouterOS Script Example:")
    print("   :local publicIP [/tool fetch url='https://api.ipify.org' output=text]")
    print("   :local url 'https://your-domain.com/update-dns'")
    print("   :local password 'your_password'")
    print("   /tool fetch url=($url) http-method=post http-data=(\"$publicIP $password\") output=none")
    print()
    print("For more information, see the README.md file.")

if __name__ == "__main__":
    test_routeros_format() 