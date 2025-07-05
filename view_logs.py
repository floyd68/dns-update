#!/usr/bin/env python3
"""
Simple DNS update log viewer.
Reads logs from dns_updates.log and displays them in a readable format.
"""

import json
import os
import sys
from datetime import datetime
from collections import Counter

def load_logs():
    """Load logs from the JSON log file."""
    logs = []
    log_file = 'dns_updates.log'
    
    if not os.path.exists(log_file):
        print(f"❌ Log file not found: {log_file}")
        print("   No DNS updates have been logged yet.")
        return []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    log_entry = json.loads(line.strip())
                    logs.append(log_entry)
                except json.JSONDecodeError as e:
                    print(f"⚠️  Invalid JSON on line {line_num}: {e}")
                    continue
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return []
    
    return logs

def show_statistics(logs):
    """Display log statistics."""
    if not logs:
        print("📊 No logs to analyze")
        return
    
    total = len(logs)
    successful = sum(1 for log in logs if log.get('status') == 'success')
    failed = sum(1 for log in logs if log.get('status') == 'error')
    unique_ips = len(set(log.get('ip_address') for log in logs if log.get('ip_address')))
    
    print("📊 DNS Update Statistics")
    print("=" * 40)
    print(f"Total updates: {total}")
    print(f"Successful: {successful} ({successful/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"Unique IP addresses: {unique_ips}")
    
    # Top IP addresses
    ip_counts = Counter(log.get('ip_address') for log in logs if log.get('ip_address'))
    if ip_counts:
        print(f"\n🏆 Top IP addresses:")
        for ip, count in ip_counts.most_common(5):
            print(f"  {ip}: {count} updates")

def show_recent_logs(logs, limit=10):
    """Display recent log entries."""
    if not logs:
        print("📋 No logs to display")
        return
    
    # Sort by timestamp (newest first)
    sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    print(f"\n📋 Recent DNS Updates (last {limit})")
    print("=" * 60)
    
    for i, log in enumerate(sorted_logs[:limit], 1):
        timestamp = log.get('timestamp', 'Unknown')
        ip_address = log.get('ip_address', 'Unknown')
        domain = log.get('domain_name', 'Unknown')
        status = log.get('status', 'Unknown')
        requester_ip = log.get('requester_ip', 'Unknown')
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_time = timestamp
        
        # Status icon
        status_icon = "✅" if status == 'success' else "❌"
        
        print(f"{i:2d}. {status_icon} {ip_address} -> {domain}")
        print(f"     Time: {formatted_time}")
        print(f"     Requester: {requester_ip}")
        
        if log.get('error_message'):
            print(f"     Error: {log['error_message']}")
        
        if log.get('change_id'):
            print(f"     Change ID: {log['change_id']}")
        
        print()

def show_failed_logs(logs, limit=5):
    """Display recent failed log entries."""
    failed_logs = [log for log in logs if log.get('status') == 'error']
    
    if not failed_logs:
        print("✅ No failed updates found")
        return
    
    # Sort by timestamp (newest first)
    sorted_failed = sorted(failed_logs, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    print(f"\n❌ Recent Failed Updates (last {limit})")
    print("=" * 50)
    
    for i, log in enumerate(sorted_failed[:limit], 1):
        timestamp = log.get('timestamp', 'Unknown')
        ip_address = log.get('ip_address', 'Unknown')
        domain = log.get('domain_name', 'Unknown')
        error_msg = log.get('error_message', 'Unknown error')
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_time = timestamp
        
        print(f"{i}. {ip_address} -> {domain}")
        print(f"   Time: {formatted_time}")
        print(f"   Error: {error_msg}")
        print()

def main():
    """Main function."""
    print("📊 DNS Update Log Viewer")
    print("=" * 30)
    
    logs = load_logs()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'stats':
            show_statistics(logs)
        elif command == 'failed':
            show_failed_logs(logs)
        elif command == 'recent':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            show_recent_logs(logs, limit)
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: stats, failed, recent [limit]")
    else:
        # Show overview
        show_statistics(logs)
        show_recent_logs(logs, 5)
        
        print("\n💡 Usage:")
        print("  python view_logs.py stats     - Show statistics")
        print("  python view_logs.py failed    - Show failed updates")
        print("  python view_logs.py recent    - Show recent updates")
        print("  python view_logs.py recent 20 - Show last 20 updates")

if __name__ == '__main__':
    main() 