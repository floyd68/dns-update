import os

class Config:
    """Configuration class for the DNS Update Service."""
    
    # Flask Configuration
    FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # AWS Configuration
    AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    # DNS Configuration
    DEFAULT_TTL = int(os.environ.get('DNS_TTL', 300))  # 5 minutes default
    HOSTED_ZONE_ID = os.environ.get('HOSTED_ZONE_ID')
    DOMAIN_NAME = os.environ.get('DOMAIN_NAME')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def validate_aws_config():
        """Validate that AWS credentials are configured."""
        if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
            raise ValueError(
                "AWS credentials not configured. Please set AWS_ACCESS_KEY_ID and "
                "AWS_SECRET_ACCESS_KEY environment variables or configure AWS CLI."
            ) 