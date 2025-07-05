#!/usr/bin/env python3
"""
Startup script for the DNS Update Service.
This script handles environment setup and starts the Flask application.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required.")
        sys.exit(1)
    print(f"Python version: {sys.version}")

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import boto3
        print("✅ All dependencies are installed.")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def setup_environment():
    """Set up environment variables if not already set."""
    env_vars = {
        'FLASK_HOST': '0.0.0.0',
        'FLASK_PORT': '5000',
        'FLASK_DEBUG': 'False',
        'AWS_DEFAULT_REGION': 'us-east-1'
    }
    
    for var, default_value in env_vars.items():
        if not os.environ.get(var):
            os.environ[var] = default_value
            print(f"Set {var}={default_value}")

def check_aws_credentials():
    """Check if AWS credentials are configured."""
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    if not aws_access_key or not aws_secret_key:
        print("⚠️  AWS credentials not found in environment variables.")
        print("Please configure AWS credentials using one of these methods:")
        print("1. Set environment variables: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        print("2. Use AWS CLI: aws configure")
        print("3. Use IAM role (if running on EC2)")
        print("\nThe service will start but DNS updates will fail without credentials.")
    else:
        print("✅ AWS credentials found in environment variables.")

def check_dns_config():
    """Check if DNS configuration is set."""
    hosted_zone_id = os.environ.get('HOSTED_ZONE_ID')
    domain_name = os.environ.get('DOMAIN_NAME')
    
    if not hosted_zone_id or not domain_name:
        print("⚠️  DNS configuration not found in environment variables.")
        print("Please set the following environment variables:")
        print("- HOSTED_ZONE_ID: Your Route53 hosted zone ID")
        print("- DOMAIN_NAME: The domain name to update")
        print("\nExample:")
        print("export HOSTED_ZONE_ID=Z1234567890ABC")
        print("export DOMAIN_NAME=api.example.com")
        return False
    else:
        print(f"✅ DNS configuration found:")
        print(f"   Hosted Zone ID: {hosted_zone_id}")
        print(f"   Domain Name: {domain_name}")
        return True

def main():
    """Main startup function."""
    print("DNS Update Service - Startup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Check AWS credentials
    check_aws_credentials()
    
    # Check DNS configuration
    check_dns_config()
    
    print("\nStarting Flask application...")
    print("=" * 40)
    
    # Import and run the Flask app
    try:
        from app import app, Config
        host = Config.FLASK_HOST
        port = Config.FLASK_PORT
        debug = Config.FLASK_DEBUG
        
        print(f"Starting server on {host}:{port}")
        print(f"Debug mode: {debug}")
        print("Press Ctrl+C to stop the server")
        
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 