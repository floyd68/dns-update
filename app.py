from flask import Flask, request, jsonify
import boto3
import os
from botocore.exceptions import ClientError
import logging
import re
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
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs, take the first one
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
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

def validate_password(request):
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

@app.route('/update-dns', methods=['POST'])
def update_dns():
    """
    Update Route53 A record via HTTP POST request.
    
    Expected plain text payload with just the IP address.
    Domain name and hosted zone are pre-configured.
    """
    try:
        # Get request data - support both RouterOS format and plain IP format
        request_data = request.get_data(as_text=True).strip()
        
        if not request_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse data - RouterOS sends "IP PASSWORD" format
        data_parts = request_data.split()
        
        if len(data_parts) == 2:
            # RouterOS format: "IP PASSWORD"
            ip_address = data_parts[0]
            password = data_parts[1]
            
            # Set the password in request headers for validation
            request.headers = request.headers.copy()
            request.headers['Authorization'] = password
            
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
        if not validate_password(request):
            return jsonify({
                'error': 'Authentication failed. Invalid or missing password.'
            }), 401
        
        # Get requester's IP address
        requester_ip = get_requester_ip()
        
        # Check if the requested IP matches the requester's IP
        if not is_ip_match_allowed(ip_address, requester_ip):
            return jsonify({
                'error': f'IP address mismatch. Requested: {ip_address}, Requester: {requester_ip}. Only updating to your own IP address is allowed.'
            }), 403
        
        # Use pre-configured values
        hosted_zone_id = Config.HOSTED_ZONE_ID
        domain_name = Config.DOMAIN_NAME
        
        if not hosted_zone_id or not domain_name:
            return jsonify({
                'error': 'Domain name or hosted zone not configured. Please set HOSTED_ZONE_ID and DOMAIN_NAME environment variables.'
            }), 500
        
        # Check if AWS client is available
        if route53_client is None:
            return jsonify({'error': 'AWS Route53 client not available. Check AWS credentials.'}), 500
        
        # Update the A record
        response = update_a_record(hosted_zone_id, domain_name, ip_address)
        
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

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting DNS Update Service on {host}:{port}")
    app.run(host=host, port=port, debug=debug) 