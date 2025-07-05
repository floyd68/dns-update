#!/usr/bin/env python3
"""
Test script for IP validation feature.
This script demonstrates how the IP validation works with different scenarios.
"""

import requests
import json
import sys
import os

def test_ip_validation():
    """Test the IP validation feature with different scenarios."""
    
    base_url = "http://localhost:5000"
    
    print("🔍 Testing IP Validation Feature")
    print("=" * 50)
    
    # Test 1: Update to requester's own IP (should succeed)
    print("\n1. Testing update to requester's own IP (should succeed):")
    try:
        response = requests.post(f"{base_url}/update-dns", data="127.0.0.1")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running. Start the service first.")
        return
    
    # Test 2: Update to different IP (should fail with 403)
    print("\n2. Testing update to different IP (should fail with 403):")
    try:
        response = requests.post(f"{base_url}/update-dns", data="8.8.8.8")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 3: Invalid IP format (should fail with 400)
    print("\n3. Testing invalid IP format (should fail with 400):")
    try:
        response = requests.post(f"{base_url}/update-dns", data="invalid-ip")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 4: Empty request (should fail with 400)
    print("\n4. Testing empty request (should fail with 400):")
    try:
        response = requests.post(f"{base_url}/update-dns", data="")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    # Test 5: Health check (should succeed)
    print("\n5. Testing health check (should succeed):")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Service not running.")
        return
    
    print("\n" + "=" * 50)
    print("📋 IP Validation Configuration Options:")
    print()
    print("To allow specific IP addresses to update any IP:")
    print("export ENABLE_IP_VALIDATION=true")
    print("export ALLOWED_IPS=192.168.1.100,10.0.0.50")
    print()
    print("To allow IPs from specific subnets:")
    print("export ENABLE_IP_VALIDATION=true")
    print("export ALLOWED_SUBNETS=192.168.1.0/24,10.0.0.0/16")
    print()
    print("To disable IP validation (not recommended for production):")
    print("export ENABLE_IP_VALIDATION=false")
    print()
    print("For more information, see the README.md file.")

if __name__ == "__main__":
    test_ip_validation() 