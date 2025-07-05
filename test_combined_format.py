#!/usr/bin/env python3
"""
Test script for combined format compatibility.
This script demonstrates how the service handles combined IP+password requests.
"""

import requests
import json
import sys
import os

def test_combined_format():
    """Test the combined format compatibility."""
    
    base_url = "http://localhost:5000"
    
    print("🔄 Testing Combined Format Compatibility")
    print("=" * 50)
    
    # Test 1: Combined format with valid password (should succeed)
    print("\n1. Testing combined format with valid password (should succeed):")
    try:
        combined_data = "127.0.0.1 test_password"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(f"{base_url}/update-dns", data=combined_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running. Start the service first.")
        return
    
    # Test 2: Combined format with invalid password (should fail with 401)
    print("\n2. Testing combined format with invalid password (should fail with 401):")
    try:
        combined_data = "127.0.0.1 wrong_password"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(f"{base_url}/update-dns", data=combined_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 3: Combined format with invalid IP (should fail with 400)
    print("\n3. Testing combined format with invalid IP (should fail with 400):")
    try:
        combined_data = "invalid_ip test_password"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(f"{base_url}/update-dns", data=combined_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 4: Combined format with too many parts (should fail with 400)
    print("\n4. Testing combined format with too many parts (should fail with 400):")
    try:
        combined_data = "127.0.0.1 test_password extra_part"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(f"{base_url}/update-dns", data=combined_data, headers=headers)
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
    print("📋 Combined Format Features:")
    print()
    print("✅ Supported formats:")
    print("   - Combined: 'IP PASSWORD'")
    print("   - Plain IP: 'IP' (with headers)")
    print()
    print("🔧 Example Usage:")
    print("   curl -X POST https://your-domain.com/update-dns \\")
    print("     -H 'Content-Type: text/plain' \\")
    print("     -d '203.0.113.10 your_password'")
    print()
    print("For more information, see the README.md file.")

if __name__ == "__main__":
    test_combined_format() 