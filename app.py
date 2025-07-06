from flask import Flask, request, jsonify, render_template
import boto3
import os
import sys
from botocore.exceptions import ClientError
import logging
import re
import json
from datetime import datetime, timedelta, timezone
from config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Validate AWS configuration on startup
try:
    Config.validate_aws_config()
    # AWS Route53 client
    route53_client = boto3.client('route53')
    logger.info("AWS Route53 client initialized successfully")
except ValueError as e:
    logger.error(f"AWS configuration error: {e}")
    route53_client = None

def is_valid_ip(ip_address):
    """
    Validate IP address format (IPv4).
    """
    # Basic IPv4 validation
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(ip_pattern, ip_address):
        return False
    
    # Check each octet is in valid range (0-255)
    try:
        octets = ip_address.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)
    except ValueError:
        return False

def get_requester_ip():
    """
    Get the IP address of the requester, handling proxy headers.
    """
    # Check for proxy headers first (X-Forwarded-For, X-Real-IP)
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return x_forwarded_for.split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        # Fall back to direct connection IP
        return request.remote_addr

def is_ip_match_allowed(requested_ip, requester_ip):
    """
    Check if the requested IP address is allowed to be updated.
    Returns True if the update is allowed, False otherwise.
    """
    # If IP validation is disabled, allow all updates
    if not Config.ENABLE_IP_VALIDATION:
        return True
    
    # Check if the requested IP matches the requester's IP
    if requested_ip == requester_ip:
        return True
    
    # Check if the requester's IP is in the allowed list
    if Config.ALLOWED_IPS and requester_ip in Config.ALLOWED_IPS:
        return True
    
    # Check if the requester's IP is in allowed subnets
    if Config.ALLOWED_SUBNETS:
        for subnet in Config.ALLOWED_SUBNETS:
            if is_ip_in_subnet(requester_ip, subnet):
                return True
    
    return False

def is_ip_in_subnet(ip, subnet):
    """
    Check if an IP address is within a subnet (CIDR notation).
    """
    try:
        import ipaddress
        ip_obj = ipaddress.ip_address(ip)
        subnet_obj = ipaddress.ip_network(subnet, strict=False)
        return ip_obj in subnet_obj
    except ValueError:
        # If subnet parsing fails, return False
        return False

def validate_password(request, password_from_body=None):
    """
    Validate the password from the request.
    Returns True if password is valid or authentication is disabled, False otherwise.
    """
    # If password authentication is disabled, allow all requests
    if not Config.ENABLE_PASSWORD_AUTH:
        return True
    
    # If no password is configured, allow all requests
    if not Config.AUTH_PASSWORD:
        return True
    
    # Check password from combined format (passed as parameter)
    if password_from_body:
        return password_from_body == Config.AUTH_PASSWORD
    
    # Check for password in Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header:
        # Support both "Bearer password" and "password" formats
        if auth_header.startswith('Bearer '):
            password = auth_header[7:]  # Remove "Bearer " prefix
        else:
            password = auth_header
        return password == Config.AUTH_PASSWORD
    
    # Check for password in X-Auth-Password header
    password_header = request.headers.get('X-Auth-Password')
    if password_header:
        return password_header == Config.AUTH_PASSWORD
    
    # Check for password in query parameter
    password_param = request.args.get('password')
    if password_param:
        return password_param == Config.AUTH_PASSWORD
    
    return False

def log_dns_update(ip_address, requester_ip, domain_name, status, change_id=None, error_message=None, auth_method=None):
    """
    Log DNS update attempt to JSON log file.
    """
    try:
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'ip_address': ip_address,
            'requester_ip': requester_ip,
            'domain_name': domain_name,
            'status': status,
            'change_id': change_id,
            'error_message': error_message,
            'auth_method': auth_method,
            'user_agent': request.headers.get('User-Agent', '')
        }
        
        # Get log file path from config or use default
        log_file = os.environ.get('DNS_LOG_FILE', 'dns_updates.log')
        
        # Try to write to the specified log file
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
                f.flush()  # Ensure data is written to disk immediately
                os.fsync(f.fileno())  # Force sync to disk
            logger.info(f"DNS update logged: {ip_address} -> {domain_name} ({status})")
        except (IOError, OSError) as e:
            # If the specified log file fails, try writing to /tmp
            if log_file != '/tmp/dns_updates.log':
                logger.warning(f"Failed to write to {log_file}: {e}. Trying /tmp/dns_updates.log")
                try:
                    with open('/tmp/dns_updates.log', 'a', encoding='utf-8') as f:
                        f.write(json.dumps(log_entry) + '\n')
                        f.flush()  # Ensure data is written to disk immediately
                        os.fsync(f.fileno())  # Force sync to disk
                    logger.info(f"DNS update logged to /tmp/dns_updates.log: {ip_address} -> {domain_name} ({status})")
                except (IOError, OSError) as tmp_error:
                    logger.error(f"Failed to write to /tmp/dns_updates.log: {tmp_error}")
                    # Log to stderr as fallback
                    print(f"DNS_LOG_FALLBACK: {json.dumps(log_entry)}", file=sys.stderr)
            else:
                logger.error(f"Failed to write to {log_file}: {e}")
                # Log to stderr as fallback
                print(f"DNS_LOG_FALLBACK: {json.dumps(log_entry)}", file=sys.stderr)
                
    except Exception as e:
        logger.error(f"Failed to log DNS update: {e}")
        # Log to stderr as final fallback
        try:
            fallback_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'ip_address': ip_address,
                'requester_ip': requester_ip,
                'domain_name': domain_name,
                'status': status,
                'error': f'Logging failed: {str(e)}'
            }
            print(f"DNS_LOG_FALLBACK: {json.dumps(fallback_entry)}", file=sys.stderr)
        except:
            pass

def get_auth_method(request, password_from_body=None):
    """
    Determine the authentication method used.
    """
    if password_from_body:
        return 'combined'
    elif request.headers.get('Authorization'):
        return 'header'
    elif request.headers.get('X-Auth-Password'):
        return 'header'
    elif request.args.get('password'):
        return 'query'
    else:
        return None

def read_logs_from_single_file(file_path):
    """
    Read logs from a single file.
    Returns a list of log entries.
    """
    logs = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue  # Skip invalid lines
        except (IOError, OSError) as e:
            logger.warning(f"Failed to read from {file_path}: {e}")
    return logs

def read_logs_from_file():
    """
    Read logs from file with fallback logic.
    Returns a list of log entries.
    """
    log_file = os.environ.get('DNS_LOG_FILE', 'dns_updates.log')
    
    # Try to read from the configured log file
    logs = read_logs_from_single_file(log_file)
    
    # If no logs found in configured file, try /tmp/dns_updates.log
    if not logs and log_file != '/tmp/dns_updates.log':
        tmp_log_file = '/tmp/dns_updates.log'
        logs = read_logs_from_single_file(tmp_log_file)
    
    return logs

@app.route('/update-dns', methods=['POST'])
def update_dns():
    """
    Update Route53 A record via HTTP POST request.
    
    Expected plain text payload with just the IP address.
    Domain name and hosted zone are pre-configured.
    """
    try:
        # Get request data - support both combined format and plain IP format
        request_data = request.get_data(as_text=True).strip()
        
        if not request_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse data - support "IP PASSWORD" format or plain IP
        data_parts = request_data.split()
        
        if len(data_parts) == 2:
            # Combined format: "IP PASSWORD"
            ip_address = data_parts[0]
            password = data_parts[1]
            
        elif len(data_parts) == 1:
            # Plain IP format (existing behavior)
            ip_address = data_parts[0]
            password = None
        else:
            return jsonify({'error': 'Invalid data format. Expected "IP PASSWORD" or just "IP"'}), 400
        
        # Validate IP address format (basic validation)
        if not is_valid_ip(ip_address):
            return jsonify({'error': 'Invalid IP address format'}), 400
        
        # Validate password authentication
        if not validate_password(request, password):
            auth_method = get_auth_method(request, password)
            log_dns_update(ip_address, get_requester_ip(), Config.DOMAIN_NAME, 'error', 
                          error_message='Authentication failed', auth_method=auth_method)
            return jsonify({
                'error': 'Authentication failed. Invalid or missing password.'
            }), 401
        
        # Get requester's IP address
        requester_ip = get_requester_ip()
        
        # Check if the requested IP matches the requester's IP
        if not is_ip_match_allowed(ip_address, requester_ip):
            auth_method = get_auth_method(request, password)
            log_dns_update(ip_address, requester_ip, Config.DOMAIN_NAME, 'error',
                          error_message=f'IP address mismatch. Requested: {ip_address}, Requester: {requester_ip}', 
                          auth_method=auth_method)
            return jsonify({
                'error': f'IP address mismatch. Requested: {ip_address}, Requester: {requester_ip}. Only updating to your own IP address is allowed.'
            }), 403
        
        # Use pre-configured values
        hosted_zone_id = Config.HOSTED_ZONE_ID
        domain_name = Config.DOMAIN_NAME
        
        if not hosted_zone_id or not domain_name:
            auth_method = get_auth_method(request, password)
            log_dns_update(ip_address, requester_ip, domain_name or 'unknown', 'error',
                          error_message='Domain name or hosted zone not configured', auth_method=auth_method)
            return jsonify({
                'error': 'Domain name or hosted zone not configured. Please set HOSTED_ZONE_ID and DOMAIN_NAME environment variables.'
            }), 500
        
        # Check if AWS client is available
        if route53_client is None:
            auth_method = get_auth_method(request, password)
            log_dns_update(ip_address, requester_ip, domain_name, 'error',
                          error_message='AWS Route53 client not available', auth_method=auth_method)
            return jsonify({'error': 'AWS Route53 client not available. Check AWS credentials.'}), 500
        
        # Update the A record
        response = update_a_record(hosted_zone_id, domain_name, ip_address)
        
        # Log successful update
        auth_method = get_auth_method(request, password)
        log_dns_update(ip_address, requester_ip, domain_name, 'success', 
                      change_id=response['ChangeInfo']['Id'], auth_method=auth_method)
        
        return jsonify({
            'success': True,
            'message': f'A record for {domain_name} updated to {ip_address}',
            'change_id': response['ChangeInfo']['Id']
        }), 200
        
    except ClientError as e:
        logger.error(f"AWS error: {e}")
        return jsonify({'error': f'AWS error: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

def update_a_record(hosted_zone_id, domain_name, ip_address):
    """
    Update Route53 A record with new IP address.
    """
    if route53_client is None:
        raise ValueError("AWS Route53 client not available")
    
    # Prepare the change batch
    change_batch = {
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': domain_name,
                    'Type': 'A',
                    'TTL': 300,  # 5 minutes TTL
                    'ResourceRecords': [
                        {
                            'Value': ip_address
                        }
                    ]
                }
            }
        ]
    }
    
    # Submit the change request
    response = route53_client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch=change_batch
    )
    
    logger.info(f"DNS update submitted: {response['ChangeInfo']['Id']}")
    return response

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'DNS Update Service'}), 200

@app.route('/logs', methods=['GET'])
def logs_page():
    """DNS logs web interface."""
    return render_template('logs.html')

@app.route('/api/logs', methods=['GET'])
def api_logs():
    """API endpoint for retrieving DNS logs with filtering and pagination."""
    try:
        page = int(request.args.get('page', 1))
        per_page = 50
        filter_type = request.args.get('filter', 'all')
        search = request.args.get('search', '').strip()
        
        # Read logs from file using helper function
        logs = read_logs_from_file()
        
        # Apply filters
        filtered_logs = []
        for log in logs:
            # Status filter
            if filter_type == 'success' and log.get('status') != 'success':
                continue
            elif filter_type == 'error' and log.get('status') != 'error':
                continue
            elif filter_type == 'today':
                log_date = datetime.fromisoformat(log.get('timestamp', '')).date()
                if log_date != datetime.now(timezone.utc).date():
                    continue
            elif filter_type == 'week':
                log_date = datetime.fromisoformat(log.get('timestamp', ''))
                if log_date < datetime.now(timezone.utc) - timedelta(days=7):
                    continue
            
            # Search filter
            if search:
                search_lower = search.lower()
                if not any(search_lower in str(log.get(field, '')).lower() 
                          for field in ['ip_address', 'requester_ip', 'domain_name', 'error_message']):
                    continue
            
            filtered_logs.append(log)
        
        # Sort by timestamp (newest first)
        filtered_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Apply pagination
        total_count = len(filtered_logs)
        total_pages = (total_count + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_logs = filtered_logs[start_idx:end_idx]
        
        # Calculate statistics using the same logs
        successful_count = sum(1 for log in logs if log.get('status') == 'success')
        failed_count = sum(1 for log in logs if log.get('status') == 'error')
        unique_ips = len(set(log.get('ip_address') for log in logs if log.get('ip_address')))
        
        stats = {
            'total': len(logs),
            'successful': successful_count,
            'failed': failed_count,
            'unique_ips': unique_ips
        }
        
        return jsonify({
            'success': True,
            'logs': paginated_logs,
            'stats': stats,
            'current_page': page,
            'total_pages': total_pages,
            'total_count': total_count
        })
        
    except Exception as e:
        logger.error(f"Error retrieving logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """API endpoint for getting DNS update statistics."""
    try:
        # Read logs from file using helper function
        logs = read_logs_from_file()
        
        # Calculate basic stats
        total = len(logs)
        successful = sum(1 for log in logs if log.get('status') == 'success')
        failed = sum(1 for log in logs if log.get('status') == 'error')
        unique_ips = len(set(log.get('ip_address') for log in logs if log.get('ip_address')))
        
        # Get recent activity (last 24 hours)
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        recent_updates = sum(1 for log in logs 
                           if datetime.fromisoformat(log.get('timestamp', '')) >= yesterday)
        
        # Get top IP addresses
        ip_counts = {}
        for log in logs:
            ip = log.get('ip_address')
            if ip:
                ip_counts[ip] = ip_counts.get(ip, 0) + 1
        
        top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_ips_data = [{'ip': ip, 'count': count} for ip, count in top_ips]
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'successful': successful,
                'failed': failed,
                'unique_ips': unique_ips,
                'recent_updates': recent_updates,
                'top_ips': top_ips_data
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting DNS Update Service on {host}:{port}")
    app.run(host=host, port=port, debug=debug) 