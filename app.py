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

@app.route('/update-dns', methods=['POST'])
def update_dns():
    """
    Update Route53 A record via HTTP POST request.
    
    Expected plain text payload with just the IP address.
    Domain name and hosted zone are pre-configured.
    """
    try:
        # Get plain text IP address from request body
        ip_address = request.get_data(as_text=True).strip()
        
        if not ip_address:
            return jsonify({'error': 'No IP address provided'}), 400
        
        # Validate IP address format (basic validation)
        if not is_valid_ip(ip_address):
            return jsonify({'error': 'Invalid IP address format'}), 400
        
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