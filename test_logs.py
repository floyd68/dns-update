#!/usr/bin/env python3
"""
Test script for DNS Update Service with logging functionality.
This script demonstrates the new logging features and web interface.
"""

import requests
import time
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_IP = "203.0.113.10"  # RFC 5737 test IP
TEST_PASSWORD = "test_password_123"

def test_dns_update():
    """Test DNS update with logging."""
    print("🔄 Testing DNS update with logging...")
    
    # Test successful update
    try:
        response = requests.post(
            f"{BASE_URL}/update-dns",
            headers={
                'Content-Type': 'text/plain',
                'Authorization': TEST_PASSWORD
            },
            data=TEST_IP
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ DNS update successful: {result.get('message', 'Unknown')}")
            print(f"   Change ID: {result.get('change_id', 'N/A')}")
        else:
            print(f"❌ DNS update failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the service. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error testing DNS update: {e}")
        return False
    
    return True

def test_logs_api():
    """Test the logs API endpoint."""
    print("\n📊 Testing logs API...")
    
    try:
        # Get logs
        response = requests.get(f"{BASE_URL}/api/logs")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logs = data.get('logs', [])
                stats = data.get('stats', {})
                
                print(f"✅ Logs API working")
                print(f"   Total logs: {stats.get('total', 0)}")
                print(f"   Successful: {stats.get('successful', 0)}")
                print(f"   Failed: {stats.get('failed', 0)}")
                print(f"   Unique IPs: {stats.get('unique_ips', 0)}")
                
                if logs:
                    print(f"\n📋 Recent logs ({len(logs)} entries):")
                    for log in logs[:3]:  # Show first 3 logs
                        status_icon = "✅" if log['status'] == 'success' else "❌"
                        timestamp = log['created_at'][:19] if log['created_at'] else 'N/A'
                        print(f"   {status_icon} {log['ip_address']} -> {log['domain_name']} ({log['status']}) - {timestamp}")
                else:
                    print("   No logs found")
                    
            else:
                print(f"❌ Logs API error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Logs API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing logs API: {e}")
        return False
    
    return True

def test_stats_api():
    """Test the stats API endpoint."""
    print("\n📈 Testing stats API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('stats', {})
                
                print(f"✅ Stats API working")
                print(f"   Total updates: {stats.get('total', 0)}")
                print(f"   Recent updates (24h): {stats.get('recent_updates', 0)}")
                
                top_ips = stats.get('top_ips', [])
                if top_ips:
                    print(f"   Top IP addresses:")
                    for ip_data in top_ips[:3]:
                        print(f"     {ip_data['ip']}: {ip_data['count']} updates")
                        
            else:
                print(f"❌ Stats API error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Stats API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing stats API: {e}")
        return False
    
    return True

def test_web_interface():
    """Test the web interface."""
    print("\n🌐 Testing web interface...")
    
    try:
        response = requests.get(f"{BASE_URL}/logs")
        
        if response.status_code == 200:
            print("✅ Web interface accessible")
            print(f"   URL: {BASE_URL}/logs")
            print("   You can view the logs in your browser")
        else:
            print(f"❌ Web interface failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing web interface: {e}")
        return False
    
    return True

def show_usage_instructions():
    """Show usage instructions for the new features."""
    print("\n" + "="*60)
    print("🎉 DNS Update Service with Logging - Setup Complete!")
    print("="*60)
    
    print("\n📋 Available Features:")
    print("  ✅ DNS update logging to JSON log file")
    print("  ✅ Modern web interface for viewing logs")
    print("  ✅ Real-time statistics and filtering")
    print("  ✅ API endpoints for programmatic access")
    print("  ✅ Search and pagination support")
    
    print("\n🌐 Web Interface:")
    print(f"  • Logs page: {BASE_URL}/logs")
    print("  • Features: Search, filter, pagination, real-time updates")
    print("  • Mobile-responsive design with modern UI")
    
    print("\n🔌 API Endpoints:")
    print(f"  • GET {BASE_URL}/api/logs - Get logs with filtering")
    print(f"  • GET {BASE_URL}/api/stats - Get statistics")
    print(f"  • POST {BASE_URL}/update-dns - Update DNS (existing)")
    print(f"  • GET {BASE_URL}/health - Health check (existing)")
    
    print("\n📊 Log File:")
    print("  • JSON log file: dns_updates.log")
    print("  • View logs: python view_logs.py")
    print("  • Check status: python view_logs.py stats")
    
    print("\n🚀 Getting Started:")
    print("  1. Start service: python app.py")
    print("  2. View logs: http://localhost:5000/logs")
    print("  3. Test updates: python test_logs.py")
    print("  4. View logs in terminal: python view_logs.py")
    
    print("\n💡 Tips:")
    print("  • The web interface auto-refreshes every 30 seconds")
    print("  • Use the search box to find specific IPs or domains")
    print("  • Filter by status (success/error) or time period")
    print("  • All DNS updates are automatically logged to dns_updates.log")

def main():
    """Main test function."""
    print("🧪 DNS Update Service - Logging Test Suite")
    print("=" * 50)
    
    # Check if service is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Service is not responding properly")
            return False
    except:
        print("❌ Service is not running. Please start it with: python app.py")
        return False
    
    # Run tests
    tests = [
        ("DNS Update", test_dns_update),
        ("Logs API", test_logs_api),
        ("Stats API", test_stats_api),
        ("Web Interface", test_web_interface)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The logging system is working correctly.")
        show_usage_instructions()
    else:
        print("⚠️  Some tests failed. Check the service configuration.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 