# DNS Update Service - Logging Endpoints Configuration

This document describes the new logging and statistics endpoints that have been added to the nginx configuration.

## New Endpoints

### 1. Web Interface (`/logs`)
- **Purpose**: Modern web interface for viewing DNS update logs
- **Method**: GET only
- **Access**: Restricted by IP whitelist (configurable)
- **Features**: 
  - Real-time statistics dashboard
  - Search and filtering capabilities
  - Mobile-responsive design
  - Auto-refresh every 30 seconds

### 2. Logs API (`/api/logs`)
- **Purpose**: Programmatic access to DNS update logs
- **Method**: GET only
- **Access**: Restricted by IP whitelist (configurable)
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `filter`: Filter type - `all`, `success`, `error`, `today`, `week`
  - `search`: Search term for IP, domain, or error message

### 3. Statistics API (`/api/stats`)
- **Purpose**: DNS update statistics and analytics
- **Method**: GET only
- **Access**: Restricted by IP whitelist (configurable)
- **Returns**: Total updates, success/failure counts, unique IPs, recent activity

## Security Configuration

### IP Whitelist (Optional)
The logging endpoints include optional IP whitelist protection. To enable:

1. Edit the nginx configuration file:
   ```bash
   sudo nano /etc/nginx/sites-available/dns-update
   ```

2. Uncomment and modify the IP whitelist lines:
   ```nginx
   # DNS Logs Web Interface (restricted access)
   location /logs {
       # IP Whitelist for web interface
       allow 192.168.1.0/24;    # Your local network
       allow 10.0.0.0/8;        # Private network
       deny all;
       
       # ... rest of configuration
   }
   ```

3. Reload nginx:
   ```bash
   sudo systemctl reload nginx
   ```

### Rate Limiting
All endpoints inherit the rate limiting configuration:
- 10 requests per minute per IP
- Burst allowance of 20 requests

## Log Files

The nginx configuration creates separate log files for each endpoint:

- `/var/log/nginx/dns-update-logs.log` - Web interface access
- `/var/log/nginx/dns-update-logs-api.log` - Logs API access
- `/var/log/nginx/dns-update-stats-api.log` - Stats API access

## Testing the Endpoints

### Web Interface
```bash
# Access the web interface
curl https://your-domain.com/logs

# Or open in browser
open https://your-domain.com/logs
```

### Logs API
```bash
# Get all logs
curl https://your-domain.com/api/logs

# Get successful updates only
curl "https://your-domain.com/api/logs?filter=success"

# Search for specific IP
curl "https://your-domain.com/api/logs?search=192.168.1.100"

# Get logs from today
curl "https://your-domain.com/api/logs?filter=today"
```

### Statistics API
```bash
# Get statistics
curl https://your-domain.com/api/stats
```

## Configuration Files

### SSL Configuration (`dns-update.conf`)
- Includes all new endpoints with SSL/TLS
- Proper security headers
- Rate limiting enabled

### HTTP Configuration (`dns-update-http.conf`)
- Same endpoints without SSL
- Suitable for internal networks
- Security headers still applied

## Performance Optimizations

### Caching
The web interface includes caching for static assets:
```nginx
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Proxy Settings
- Keepalive connections to backend
- Optimized buffer settings
- Proper timeout configuration

## Troubleshooting

### Check nginx Configuration
```bash
sudo nginx -t
```

### View nginx Logs
```bash
# Access logs
sudo tail -f /var/log/nginx/dns-update-logs.log

# Error logs
sudo tail -f /var/log/nginx/dns-update-error.log
```

### Test Backend Service
```bash
# Test if backend is responding
curl http://localhost:5000/logs
curl http://localhost:5000/api/logs
curl http://localhost:5000/api/stats
```

## Security Considerations

1. **IP Whitelist**: Enable IP restrictions for production use
2. **Rate Limiting**: Already configured to prevent abuse
3. **Method Restrictions**: Only GET requests allowed for logging endpoints
4. **SSL/TLS**: Use HTTPS in production environments
5. **Log Rotation**: Configured to prevent log file bloat

## Integration with DNS Service

The logging endpoints work with the file-based logging system:
- Logs are stored in `dns_updates.log` (JSON format)
- No database required
- Lightweight and portable
- Easy to backup and transfer

## Monitoring

Monitor the following for optimal performance:
- nginx access logs for endpoint usage
- Backend service logs for errors
- Log file size and rotation
- Rate limiting effectiveness 