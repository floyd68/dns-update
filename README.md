# DNS Update Service

A Flask-based web service that updates Route53 DNS A records via HTTP POST requests with a simple plain text interface.

## Features

- Update Route53 A records via HTTP POST with plain text IP address
- Pre-configured domain name and hosted zone for security
- AWS Route53 integration using boto3
- IP address validation
- Health check endpoint
- Comprehensive error handling and logging
- **NEW: DNS update logging with JSON log file**
- **NEW: Modern web interface for viewing logs**
- **NEW: Real-time statistics and filtering**
- **NEW: API endpoints for programmatic log access**
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

4. (Optional) View logs from terminal:
   ```bash
   python view_logs.py
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

### 3. IP Validation Configuration (Optional)

The service includes IP address validation to prevent unauthorized DNS updates. By default, it only allows updating to the requester's own IP address.

**Default Behavior (Recommended):**
```bash
# No additional configuration needed - only allows updating to requester's IP
export ENABLE_IP_VALIDATION=true
```

**Allow Specific IP Addresses:**
```bash
# Allow specific IP addresses to update any IP
export ENABLE_IP_VALIDATION=true
export ALLOWED_IPS=192.168.1.100,10.0.0.50
```

**Allow Specific Subnets:**
```bash
# Allow IPs from specific subnets to update any IP
export ENABLE_IP_VALIDATION=true
export ALLOWED_SUBNETS=192.168.1.0/24,10.0.0.0/16
```

**Disable IP Validation (Not Recommended for Production):**
```bash
# Disable IP validation entirely
export ENABLE_IP_VALIDATION=false
```

**Combined Configuration:**
```bash
# Allow requester's own IP + specific IPs + specific subnets
export ENABLE_IP_VALIDATION=true
export ALLOWED_IPS=192.168.1.100,10.0.0.50
export ALLOWED_SUBNETS=192.168.1.0/24,10.0.0.0/16
```

### 4. Password Authentication Configuration (Optional)

The service includes password authentication as an additional security layer. By default, password authentication is enabled.

**Default Behavior (Recommended):**
```bash
# Enable password authentication
export ENABLE_PASSWORD_AUTH=true
export AUTH_PASSWORD=your_secure_password_here
```

**Disable Password Authentication (Not Recommended for Production):**
```bash
# Disable password authentication entirely
export ENABLE_PASSWORD_AUTH=false
```

**Password Authentication Methods:**

The service accepts the password in multiple ways:

1. **Authorization Header:**
   ```bash
   curl -X POST http://localhost:5000/update-dns \
     -H "Authorization: your_password" \
     -H "Content-Type: text/plain" \
     -d "192.168.1.100"
   ```

2. **Bearer Token Format:**
   ```bash
   curl -X POST http://localhost:5000/update-dns \
     -H "Authorization: Bearer your_password" \
     -H "Content-Type: text/plain" \
     -d "192.168.1.100"
   ```

3. **Custom Header:**
   ```bash
   curl -X POST http://localhost:5000/update-dns \
     -H "X-Auth-Password: your_password" \
     -H "Content-Type: text/plain" \
     -d "192.168.1.100"
   ```

4. **Query Parameter:**
   ```bash
   curl -X POST "http://localhost:5000/update-dns?password=your_password" \
     -H "Content-Type: text/plain" \
     -d "192.168.1.100"
   ```



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
- `DNS_LOG_FILE`: Path to DNS update log file (default: dns_updates.log). Logs persist across service restarts.
- `ENABLE_IP_VALIDATION`: Enable IP address validation (default: True)
- `ALLOWED_IPS`: Comma-separated list of allowed IP addresses (optional)
- `ALLOWED_SUBNETS`: Comma-separated list of allowed subnets in CIDR notation (optional)
- `ENABLE_PASSWORD_AUTH`: Enable password authentication (default: True)
- `AUTH_PASSWORD`: Password for authentication (required if ENABLE_PASSWORD_AUTH is True)
- `FLASK_SECRET_KEY`: Secret key for secure cookie management (recommended for production)

### API Endpoints

#### Update DNS A Record
**POST** `/update-dns`

**Request Body:** Plain text data in one of these formats:

1. **Plain IP address:**
   ```
   192.168.1.100
   ```

2. **Combined format (IP + Password):**
   ```
   192.168.1.100 your_password
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
    "error": "No data provided"
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

#### DNS Logs Web Interface
**GET** `/logs`

**Description:** Modern web interface for viewing DNS update logs with real-time statistics, filtering, and search capabilities.

**Authentication:** 
- Automatic access from the last successful DNS update IP
- Password-based authentication (same as DNS update service)
- Cookie-based session management (24-hour expiry)
- API access with password parameter

**Features:**
- Real-time statistics dashboard
- Search by IP address, domain, or error message
- Filter by status (success/error) or time period
- Pagination support
- Mobile-responsive design
- Auto-refresh every 30 seconds
- Secure logout functionality

#### DNS Logs API
**GET** `/api/logs`

**Query Parameters:**
- `page`: Page number (default: 1)
- `filter`: Filter type - `all`, `success`, `error`, `today`, `week` (default: all)
- `search`: Search term for IP, domain, or error message

**Response:**
```json
{
    "success": true,
    "logs": [
        {
            "id": 1,
            "ip_address": "203.0.113.10",
            "requester_ip": "192.168.1.100",
            "domain_name": "api.example.com",
            "status": "success",
            "change_id": "C1234567890ABC",
            "error_message": null,
            "auth_method": "header",
            "user_agent": "curl/7.68.0",
            "created_at": "2024-01-15T10:30:00"
        }
    ],
    "stats": {
        "total": 150,
        "successful": 145,
        "failed": 5,
        "unique_ips": 12
    },
    "current_page": 1,
    "total_pages": 3,
    "total_count": 150
}
```

#### DNS Statistics API
**GET** `/api/stats`

**Authentication:** Same as logs API - requires password or valid session

**Response:**
```json
{
    "success": true,
    "stats": {
        "total": 150,
        "successful": 145,
        "failed": 5,
        "unique_ips": 12,
        "recent_updates": 25,
        "top_ips": [
            {"ip": "203.0.113.10", "count": 45},
            {"ip": "198.51.100.20", "count": 32}
        ]
    }
}
```

#### Authentication Endpoints

**Login Page**
**GET/POST** `/login`

**Description:** Web-based login interface for accessing logs and statistics.

**Usage:**
- Visit `/login` in your browser
- Enter the same password used for DNS updates
- Login is remembered for 24 hours via secure cookies

**Logout Endpoint**
**POST** `/logout`

**Description:** Securely logout and clear authentication cookies.

**Usage:**
- Call via JavaScript: `fetch('/logout', {method: 'POST'})`
- Automatically redirects to login page

## Example Usage

### Using curl
```bash
# Method 1: Separate headers and body
curl -X POST http://localhost:5000/update-dns \
  -H "Authorization: your_password" \
  -H "Content-Type: text/plain" \
  -d "203.0.113.10"

# Method 2: Combined format (IP + password in body)
curl -X POST http://localhost:5000/update-dns \
  -H "Content-Type: text/plain" \
  -d "203.0.113.10 your_password"

# Through nginx reverse proxy (with SSL)
curl -X POST https://your-domain.com/update-dns \
  -H "Authorization: your_password" \
  -H "Content-Type: text/plain" \
  -d "203.0.113.10"

# Combined format through nginx
curl -X POST https://your-domain.com/update-dns \
  -H "Content-Type: text/plain" \
  -d "203.0.113.10 your_password"

# Using query parameter for authentication
curl -X POST "http://localhost:5000/update-dns?password=your_password" \
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

# Method 1: Separate headers and body
ip_address = "203.0.113.10"
headers = {
    'Content-Type': 'text/plain',
    'Authorization': 'your_password'
}
response = requests.post('http://localhost:5000/update-dns', data=ip_address, headers=headers)
print(response.json())

# Method 2: Combined format (IP + password in body)
combined_data = "203.0.113.10 your_password"
headers = {'Content-Type': 'text/plain'}
response = requests.post('http://localhost:5000/update-dns', data=combined_data, headers=headers)
print(response.json())

# Alternative: Using query parameter for authentication
response = requests.post('http://localhost:5000/update-dns?password=your_password', data=ip_address)
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

### Using the logging test script
```bash
python test_logs.py
```

The logging test script will:
- Test DNS updates with logging
- Verify the logs API endpoints
- Check the web interface accessibility
- Display comprehensive usage instructions

### Testing Authentication
```bash
python test_auth.py
```

The authentication test script will:
- Test access control for logs and stats pages
- Verify login/logout functionality
- Test cookie-based session management
- Validate API access with password parameter
- Test automatic access from last successful DNS update IP

### Viewing DNS Logs

#### Web Interface
```bash
# Open in your browser
http://localhost:5000/logs
```

**Authentication Features:**
- **Automatic Access**: IP addresses that successfully updated DNS records can access logs without password
- **Password Authentication**: Use the same password as DNS update service
- **Session Management**: Login remembered for 24 hours via secure cookies
- **API Access**: Use password parameter for programmatic access

**Features:**
- Real-time statistics dashboard
- Search and filter capabilities
- Mobile-responsive design
- Auto-refresh every 30 seconds
- Secure logout functionality

#### API Access
```bash
# Get all logs
curl http://localhost:5000/api/logs

# Get successful updates only
curl "http://localhost:5000/api/logs?filter=success"

# Search for specific IP
curl "http://localhost:5000/api/logs?search=203.0.113.10"

# Get statistics
curl http://localhost:5000/api/stats
```

#### Log File Management
```bash
# View logs in terminal
python view_logs.py

# Show statistics
python view_logs.py stats

# Show failed updates
python view_logs.py failed

# Show recent updates
python view_logs.py recent 20
```

#### Log File Configuration
The service supports configurable log file locations to handle read-only file systems:

```bash
# Use default location (current directory)
export DNS_LOG_FILE=dns_updates.log

# Use /tmp directory (for read-only systems)
export DNS_LOG_FILE=/tmp/dns_updates.log

# Use a writable directory
export DNS_LOG_FILE=/var/log/dns_updates.log
```

**Log File Persistence:**
- Logs are written in append mode and persist across service restarts
- The systemd service is configured to use `/opt/dns-update/logs/dns_updates.log` by default
- Log files are never automatically cleared or truncated
- Logs are immediately flushed to disk to prevent data loss during crashes
- Use log rotation tools (like logrotate) for long-term log management

**Fallback Behavior:**
- If the configured log file is not writable, the service will try `/tmp/dns_updates.log`
- If `/tmp` is also not writable, logs will be written to stderr
- The service will continue to function even if logging fails

### Combined Format Integration

The service supports sending data in the format `"IP PASSWORD"` for convenience:

**Example Usage:**
```bash
# Get public IP and update DNS in one request
curl -X POST https://your-domain.com/update-dns \
  -H "Content-Type: text/plain" \
  -d "203.0.113.10 your_password"
```

**Features:**
- Automatically parses combined format: `"IP PASSWORD"`
- Falls back to plain IP format for backward compatibility
- Supports all authentication methods (headers, query parameters, or embedded in body)
- Maintains security with password validation

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

3. **Password Authentication**: The service includes password authentication as an additional security layer:
   - By default, requires a pre-configured password for all DNS updates
   - Supports multiple authentication methods (headers, query parameters)
   - Can be disabled for testing or specific use cases
   - Use strong, unique passwords for production environments

4. **IP Validation**: The service includes IP address validation to prevent unauthorized DNS updates:
   - By default, only allows updating to the requester's own IP address
   - Can be configured to allow specific IP addresses or subnets
   - Can be disabled for testing or specific use cases
   - Handles proxy headers (X-Forwarded-For, X-Real-IP) for accurate IP detection

5. **Network Security**: 
   - Use HTTPS in production
   - Consider firewall rules to restrict access
   - Run behind a reverse proxy for additional security

6. **Input Validation**: The service validates IP address format but consider additional validation for production use.

7. **Configuration Security**: 
   - Keep AWS credentials secure
   - Use IAM roles when possible
   - Rotate access keys regularly
   - Store passwords securely and rotate them regularly

## Error Handling

The service handles various error scenarios:
- Missing or invalid IP address
- Invalid IP address format
- Authentication failure (invalid or missing password)
- IP address mismatch (requested IP doesn't match requester's IP)
- Missing DNS configuration (hosted zone ID or domain name)
- AWS Route53 API errors
- Network connectivity issues
- AWS credentials not configured

All errors are logged and appropriate HTTP status codes are returned:

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid IP, missing data) |
| 401 | Unauthorized (authentication failed) |
| 403 | Forbidden (IP address mismatch) |
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

5. **Authentication Failed (401 Unauthorized)**
   - The service requires a password by default
   - Check if you're providing the correct password
   - Verify the password is set in `AUTH_PASSWORD` environment variable
   - Use one of the supported authentication methods (headers, query parameters)
   - Set `ENABLE_PASSWORD_AUTH=false` to disable authentication (not recommended for production)

6. **IP Address Mismatch (403 Forbidden)**
   - The service only allows updating to the requester's own IP address by default
   - Check if you're requesting to update to a different IP than your own
   - Configure `ALLOWED_IPS` or `ALLOWED_SUBNETS` if you need to update to different IPs
   - Set `ENABLE_IP_VALIDATION=false` to disable this check (not recommended for production)

7. **Service Not Starting**
   - Check Python version (3.7+ required)
   - Install dependencies: `pip install -r requirements.txt`
   - Use the startup script for detailed error checking

8. **404 Error Through Nginx**
   - Ensure backend service is running on port 5000
   - Check nginx status: `sudo systemctl status nginx`
   - Verify nginx configuration: `sudo nginx -t`
   - Restart nginx: `sudo systemctl restart nginx`
   - Check nginx logs: `sudo tail -f /var/log/nginx/error.log`
   - Run troubleshooting script: `python troubleshoot_nginx.py`

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



#### Uninstallation

```bash
# Remove nginx configuration
sudo ./nginx/uninstall-nginx.sh
```

## License

This project is provided as-is for educational and development purposes. 