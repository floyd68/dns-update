#!/usr/bin/env python3
"""
Test script for the DNS Update Service.
This script demonstrates how to use the service to update Route53 A records.
"""

import requests
import json
import sys
import time

def test_health_check(base_url):
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")
        return False

def test_dns_update(base_url, ip_address):
    """Test the DNS update endpoint."""
    try:
        print(f"Updating DNS A record to {ip_address}")
        response = requests.post(
            f"{base_url}/update-dns",
            data=ip_address,
            headers={'Content-Type': 'text/plain'}
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"DNS update failed: {e}")
        return False

def main():
    """Main test function."""
    base_url = "http://localhost:5000"
    
    # Test health check first
    print("=== Testing Health Check ===")
    if not test_health_check(base_url):
        print("Health check failed. Make sure the service is running.")
        sys.exit(1)
    
    print("\n=== Testing DNS Update ===")
    
    # Get IP address from user or use default
    ip_address = input("Enter IP address (or press Enter for demo): ").strip()
    if not ip_address:
        ip_address = "192.168.1.100"  # Demo value
        print(f"Using demo IP address: {ip_address}")
    
    # Test DNS update
    success = test_dns_update(base_url, ip_address)
    
    if success:
        print("\n✅ DNS update test completed successfully!")
    else:
        print("\n❌ DNS update test failed!")
        sys.exit(1)
    
    print("\n💡 Tip: Run 'python test_ip_validation.py' to test the IP validation feature.")
    print("💡 Tip: Run 'python test_password_auth.py' to test the password authentication feature.")

if __name__ == "__main__":
    print("DNS Update Service Test Script")
    print("=" * 40)
    main() 