#!/usr/bin/env python3
"""
Troubleshooting script for nginx and backend connectivity issues.
This script helps diagnose 404 errors when posting data through nginx.
"""

import requests
import json
import sys
import os
import subprocess
import time

def check_backend_service():
    """Check if the backend service is running."""
    print("🔍 Checking Backend Service")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend service is running on port 5000")
            return True
        else:
            print(f"❌ Backend service returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend service is not running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Error checking backend service: {e}")
        return False

def check_nginx_status():
    """Check nginx status."""
    print("\n🔍 Checking Nginx Status")
    print("=" * 40)
    
    try:
        # Check if nginx is running
        result = subprocess.run(['systemctl', 'is-active', 'nginx'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Nginx is running")
        else:
            print("❌ Nginx is not running")
            return False
        
        # Check nginx configuration
        result = subprocess.run(['nginx', '-t'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Nginx configuration is valid")
        else:
            print("❌ Nginx configuration is invalid:")
            print(result.stderr)
            return False
            
        return True
    except Exception as e:
        print(f"❌ Error checking nginx: {e}")
        return False

def test_direct_backend():
    """Test direct connection to backend."""
    print("\n🔍 Testing Direct Backend Connection")
    print("=" * 40)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:5000/health", timeout=5)
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Test DNS update endpoint
        headers = {'Content-Type': 'text/plain', 'Authorization': 'test_password'}
        response = requests.post("http://localhost:5000/update-dns", 
                               data="127.0.0.1", headers=headers, timeout=10)
        print(f"DNS update: {response.status_code} - {response.json()}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_nginx_proxy():
    """Test nginx proxy connection."""
    print("\n🔍 Testing Nginx Proxy Connection")
    print("=" * 40)
    
    # Test different URLs
    test_urls = [
        "http://localhost/health",
        "http://localhost/update-dns",
        "https://localhost/health",
        "https://localhost/update-dns"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url}: {response.status_code}")
        except requests.exceptions.SSLError:
            print(f"⚠️  {url}: SSL error (expected for HTTP URLs with HTTPS)")
        except requests.exceptions.ConnectionError:
            print(f"❌ {url}: Connection refused")
        except Exception as e:
            print(f"❌ {url}: {e}")

def test_post_through_nginx():
    """Test POST request through nginx."""
    print("\n🔍 Testing POST Through Nginx")
    print("=" * 40)
    
    test_cases = [
        {
            "url": "http://localhost/update-dns",
            "data": "127.0.0.1",
            "headers": {"Content-Type": "text/plain", "Authorization": "test_password"}
        },
        {
            "url": "http://localhost/update-dns",
            "data": "127.0.0.1 test_password",
            "headers": {"Content-Type": "text/plain"}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['url']}")
        print(f"Data: {test_case['data']}")
        print(f"Headers: {test_case['headers']}")
        
        try:
            response = requests.post(test_case['url'], 
                                   data=test_case['data'], 
                                   headers=test_case['headers'], 
                                   timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except requests.exceptions.ConnectionError:
            print("❌ Connection refused")
        except Exception as e:
            print(f"❌ Error: {e}")

def check_nginx_logs():
    """Check nginx logs for errors."""
    print("\n🔍 Checking Nginx Logs")
    print("=" * 40)
    
    log_files = [
        "/var/log/nginx/error.log",
        "/var/log/nginx/dns-update-error.log",
        "/var/log/nginx/dns-update-access.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📄 {log_file}:")
            try:
                # Get last 10 lines
                result = subprocess.run(['tail', '-10', log_file], 
                                      capture_output=True, text=True, timeout=10)
                if result.stdout:
                    print(result.stdout)
                else:
                    print("(empty)")
            except Exception as e:
                print(f"Error reading log: {e}")
        else:
            print(f"❌ {log_file}: File not found")

def main():
    """Main troubleshooting function."""
    print("🔧 DNS Update Service Nginx Troubleshooting")
    print("=" * 50)
    
    # Check backend service
    backend_ok = check_backend_service()
    
    # Check nginx status
    nginx_ok = check_nginx_status()
    
    # Test direct backend
    if backend_ok:
        test_direct_backend()
    
    # Test nginx proxy
    if nginx_ok:
        test_nginx_proxy()
        test_post_through_nginx()
    
    # Check logs
    check_nginx_logs()
    
    print("\n" + "=" * 50)
    print("📋 Troubleshooting Summary:")
    print()
    if backend_ok:
        print("✅ Backend service is running")
    else:
        print("❌ Backend service is not running")
        print("   - Start the service: python app.py")
        print("   - Or use systemd: sudo systemctl start dns-update")
    
    if nginx_ok:
        print("✅ Nginx is running and configured")
    else:
        print("❌ Nginx has issues")
        print("   - Check nginx status: sudo systemctl status nginx")
        print("   - Restart nginx: sudo systemctl restart nginx")
    
    print("\n💡 Common Solutions:")
    print("1. Ensure backend service is running on port 5000")
    print("2. Check nginx configuration: sudo nginx -t")
    print("3. Restart nginx: sudo systemctl restart nginx")
    print("4. Check firewall settings")
    print("5. Verify domain name in nginx config matches your domain")

if __name__ == "__main__":
    main() 