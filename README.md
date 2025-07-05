# DNS Update Service

A Flask-based web service that updates Route53 DNS A records via HTTP POST requests with a simple plain text interface.

## Features

- Update Route53 A records via HTTP POST with plain text IP address
- Pre-configured domain name and hosted zone for security
- AWS Route53 integration using boto3
- IP address validation
- Health check endpoint
- Comprehensive error handling and logging
- Docker support for easy deployment

## Prerequisites

- Python 3.7+
- AWS credentials configured with Route53 permissions
- Route53 hosted zone ID
- Domain name to update

## Installation

1. Clone or download this project
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### 1. AWS Credentials

#### Option 1: AWS CLI Configuration
```bash
aws configure
```

#### Option 2: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

#### Option 3: IAM Role (for EC2 instances)
If running on an EC2 instance, attach an IAM role with Route53 permissions.

### 2. DNS Configuration

Set the required environment variables for your domain:

```bash
export HOSTED_ZONE_ID=Z1234567890ABC
export DOMAIN_NAME=api.example.com
```

**How to find your Hosted Zone ID:**
1. Go to AWS Route53 Console
2. Navigate to "Hosted zones"
3. Click on your domain
4. Copy the "Hosted zone ID" (starts with "Z")

**Domain Name Format:**
- Use the full domain name (e.g., `api.example.com`)
- The service will update the A record for this exact domain

## Usage

### Starting the Service

#### Option 1: Direct Python
```bash
python app.py
```

#### Option 2: Using the startup script (recommended)
```bash
python start.py
```

The startup script will:
- Check Python version compatibility
- Validate dependencies
- Verify AWS credentials
- Check DNS configuration
- Start the service with proper error handling

#### Option 3: Systemd Service (Production)
```bash
# Install as systemd service
sudo ./install-service.sh

# Edit configuration
sudo nano /etc/dns-update/env

# Start the service
sudo systemctl start dns-update

# Enable auto-start on boot
sudo systemctl enable dns-update
```

#### Option 4: With Nginx Reverse Proxy (Recommended for Production)
```bash
# Install the DNS update service
sudo ./install-service.sh

# Install nginx reverse proxy
sudo ./nginx/install-nginx.sh

# Configure the DNS service
sudo nano /etc/dns-update/env

# Start both services
sudo systemctl start dns-update
sudo systemctl start nginx
```

The service will start on `http://0.0.0.0:5000` by default.

### Environment Variables

#### Required Variables
- `HOSTED_ZONE_ID`: Route53 hosted zone ID (required)
- `DOMAIN_NAME`: Domain name to update (required)

#### Optional Variables
- `FLASK_HOST`: Host to bind to (default: 0.0.0.0)
- `FLASK_PORT`: Port to bind to (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (default: False)
- `AWS_DEFAULT_REGION`: AWS region (default: us-east-1)
- `DNS_TTL`: TTL for DNS records in seconds (default: 300)
- `LOG_LEVEL`: Logging level (default: INFO)

### API Endpoints

#### Update DNS A Record
**POST** `/update-dns`

**Request Body:** Plain text IP address
```
192.168.1.100
```

**Success Response:**
```json
{
    "success": true,
    "message": "A record for example.com updated to 192.168.1.100",
    "change_id": "C1234567890ABC"
}
```

**Error Response:**
```json
{
    "error": "No IP address provided"
}
```

#### Health Check
**GET** `/health`

**Response:**
```json
{
    "status": "healthy",
    "service": "DNS Update Service"
}
```

## Example Usage

### Using curl
```bash
# Direct access (if running without nginx)
curl -X POST http://localhost:5000/update-dns \
  -H "Content-Type: text/plain" \
  -d "203.0.113.10"

# Through nginx reverse proxy (with SSL)
curl -X POST https://your-domain.com/update-dns \
  -H "Content-Type: text/plain" \
  -d "203.0.113.10"

# Through nginx reverse proxy (HTTP only)
curl -X POST http://your-domain.com/update-dns \
  -H "Content-Type: text/plain" \
  -d "203.0.113.10"

# Health check (SSL)
curl https://your-domain.com/health

# Health check (HTTP)
curl http://your-domain.com/health
```

### Using Python requests
```python
import requests

# Update DNS A record
ip_address = "203.0.113.10"
response = requests.post('http://localhost:5000/update-dns', data=ip_address)
print(response.json())

# Check service health
health_response = requests.get('http://localhost:5000/health')
print(health_response.json())
```

### Using the test script
```bash
python test_dns_update.py
```

The test script will:
- Check if the service is running
- Prompt for an IP address (or use demo value)
- Test the DNS update functionality
- Display the results

### Using the service manager (if installed as systemd service)
```bash
# Show service status
sudo ./service-manager.sh status

# Start the service
sudo ./service-manager.sh start

# View logs
sudo ./service-manager.sh logs

# Test the service
sudo ./service-manager.sh test
```

## Security Considerations

1. **Authentication**: This service has no built-in authentication. Consider adding API keys or other authentication mechanisms for production use.

2. **Authorization**: Ensure your AWS credentials have minimal required permissions for Route53 operations:
   - `route53:ChangeResourceRecordSets`
   - `route53:GetChange`

3. **Network Security**: 
   - Use HTTPS in production
   - Consider firewall rules to restrict access
   - Run behind a reverse proxy for additional security

4. **Input Validation**: The service validates IP address format but consider additional validation for production use.

5. **Configuration Security**: 
   - Keep AWS credentials secure
   - Use IAM roles when possible
   - Rotate access keys regularly

## Error Handling

The service handles various error scenarios:
- Missing or invalid IP address
- Invalid IP address format
- Missing DNS configuration (hosted zone ID or domain name)
- AWS Route53 API errors
- Network connectivity issues
- AWS credentials not configured

All errors are logged and appropriate HTTP status codes are returned:

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid IP, missing data) |
| 500 | Server Error (AWS errors, configuration issues) |

## Logging

The service logs all DNS update operations and errors. Logs include:
- DNS update requests
- AWS API responses
- Error details
- Service startup information

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   - Ensure AWS credentials are properly configured
   - Check environment variables or AWS CLI configuration
   - Verify IAM permissions include Route53 access

2. **DNS Configuration Missing**
   - Set `HOSTED_ZONE_ID` environment variable
   - Set `DOMAIN_NAME` environment variable
   - Use the startup script to validate configuration

3. **Route53 Permission Denied**
   - Verify IAM permissions include `Route53:ChangeResourceRecordSets`
   - Check hosted zone ID is correct
   - Ensure the domain exists in the specified hosted zone

4. **Invalid IP Address**
   - Ensure IP address is in valid IPv4 format (e.g., 192.168.1.100)
   - Check for extra spaces or characters

5. **Service Not Starting**
   - Check Python version (3.7+ required)
   - Install dependencies: `pip install -r requirements.txt`
   - Use the startup script for detailed error checking

### Debug Mode

Enable debug mode for detailed error information:
```bash
export FLASK_DEBUG=true
python app.py
```

### Using Docker

If using Docker, ensure environment variables are passed:
```bash
docker run -e HOSTED_ZONE_ID=Z1234567890ABC \
           -e DOMAIN_NAME=api.example.com \
           -e AWS_ACCESS_KEY_ID=your_key \
           -e AWS_SECRET_ACCESS_KEY=your_secret \
           -p 5000:5000 dns-update-service
```

## Deployment Options

### Option 1: Systemd Service (Recommended for Production)

#### Installation
```bash
# Install as systemd service
sudo ./install-service.sh

# Configure the service
sudo nano /etc/dns-update/env

# Start and enable the service
sudo systemctl start dns-update
sudo systemctl enable dns-update
```

#### Management
```bash
# Use the service manager for easy management
sudo ./service-manager.sh status
sudo ./service-manager.sh start
sudo ./service-manager.sh stop
sudo ./service-manager.sh restart
sudo ./service-manager.sh logs
sudo ./service-manager.sh test

# Or use systemctl directly
sudo systemctl status dns-update
sudo systemctl start dns-update
sudo systemctl stop dns-update
sudo systemctl restart dns-update
sudo journalctl -u dns-update -f
```

#### Uninstallation
```bash
sudo ./uninstall-service.sh
```

### Option 2: Docker Deployment

#### Using Docker Compose (Recommended)

1. Create a `.env` file with your configuration:
```bash
HOSTED_ZONE_ID=Z1234567890ABC
DOMAIN_NAME=api.example.com
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

2. Build and run:
```bash
docker-compose up --build
```

#### Using Docker directly

```bash
# Build the image
docker build -t dns-update-service .

# Run with environment variables
docker run -d \
  --name dns-updater \
  -p 5000:5000 \
  -e HOSTED_ZONE_ID=Z1234567890ABC \
  -e DOMAIN_NAME=api.example.com \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  dns-update-service
```

### Option 3: Nginx Reverse Proxy Setup

The nginx reverse proxy provides:
- **SSL/TLS termination** with automatic certificate management
- **Rate limiting** to prevent abuse
- **Security headers** for enhanced protection
- **Load balancing** capabilities
- **Access control** and IP whitelisting
- **Logging and monitoring** capabilities

#### Installation

```bash
# Install nginx reverse proxy
sudo ./nginx/install-nginx.sh

# The script will:
# - Install nginx and certbot
# - Configure SSL certificates (Let's Encrypt, self-signed, or HTTP-only)
# - Set up security headers and rate limiting
# - Configure firewall rules
# - Set up log rotation
```

**SSL Options:**
1. **Let's Encrypt**: Free SSL certificates (requires public domain)
2. **Self-signed**: For testing/internal use
3. **HTTP-only**: No SSL, for internal networks (not recommended for production)

#### Configuration Features

- **SSL/TLS**: Automatic Let's Encrypt certificates, self-signed, or HTTP-only
- **Rate Limiting**: 10 requests per minute per IP
- **Security Headers**: HSTS, CSP, XSS protection (even for HTTP)
- **Access Control**: IP whitelisting for health checks
- **Method Restriction**: Only POST requests to `/update-dns`
- **Content-Type Validation**: Only accepts `text/plain`

#### Management

```bash
# Check nginx status
sudo systemctl status nginx

# Reload configuration
sudo systemctl reload nginx

# View logs
sudo tail -f /var/log/nginx/dns-update-access.log
sudo tail -f /var/log/nginx/dns-update-error.log

# Test SSL certificate
sudo certbot certificates

# Renew SSL certificate
sudo certbot renew
```

#### Protocol Switching

```bash
# Check current mode
sudo ./nginx/switch-protocol.sh status

# Switch to HTTP mode
sudo ./nginx/switch-protocol.sh http

# Switch to HTTPS mode
sudo ./nginx/switch-protocol.sh https
```

#### Uninstallation

```bash
# Remove nginx configuration
sudo ./nginx/uninstall-nginx.sh
```

## License

This project is provided as-is for educational and development purposes. 