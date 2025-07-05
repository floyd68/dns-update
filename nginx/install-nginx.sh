#!/bin/bash

# Nginx Reverse Proxy Installation Script for DNS Update Service
# This script sets up nginx as a reverse proxy with SSL

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NGINX_CONF_DIR="/etc/nginx"
SITES_AVAILABLE="$NGINX_CONF_DIR/sites-available"
SITES_ENABLED="$NGINX_CONF_DIR/sites-enabled"
SSL_DIR="/etc/ssl"
DOMAIN_NAME=""
CERT_EMAIL=""

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Function to get user input
get_domain_name() {
    read -p "Enter your domain name (e.g., dns-api.example.com): " DOMAIN_NAME
    if [ -z "$DOMAIN_NAME" ]; then
        print_error "Domain name is required"
        exit 1
    fi
}

get_email() {
    read -p "Enter your email address for SSL certificate: " CERT_EMAIL
    if [ -z "$CERT_EMAIL" ]; then
        print_error "Email address is required for SSL certificate"
        exit 1
    fi
}

# Function to install nginx
install_nginx() {
    print_status "Installing nginx..."
    
    if command -v apt-get > /dev/null 2>&1; then
        # Debian/Ubuntu
        apt-get update
        apt-get install -y nginx certbot python3-certbot-nginx
    elif command -v yum > /dev/null 2>&1; then
        # CentOS/RHEL
        yum install -y nginx certbot python3-certbot-nginx
    elif command -v dnf > /dev/null 2>&1; then
        # Fedora
        dnf install -y nginx certbot python3-certbot-nginx
    else
        print_error "Unsupported package manager"
        exit 1
    fi
    
    print_status "Nginx installed successfully"
}

# Function to configure nginx
configure_nginx() {
    print_status "Configuring nginx..."
    
    # Create nginx configuration
    cp nginx/dns-update.conf "$SITES_AVAILABLE/dns-update"
    
    # Replace domain placeholder
    sed -i "s/your-domain.com/$DOMAIN_NAME/g" "$SITES_AVAILABLE/dns-update"
    
    # Create symlink
    if [ -L "$SITES_ENABLED/dns-update" ]; then
        rm "$SITES_ENABLED/dns-update"
    fi
    ln -s "$SITES_AVAILABLE/dns-update" "$SITES_ENABLED/"
    
    # Remove default site if it exists
    if [ -L "$SITES_ENABLED/default" ]; then
        rm "$SITES_ENABLED/default"
    fi
    
    # Test nginx configuration
    if nginx -t; then
        print_status "Nginx configuration is valid"
    else
        print_error "Nginx configuration is invalid"
        exit 1
    fi
    
    # Reload nginx
    systemctl reload nginx
    print_status "Nginx configured successfully"
}

# Function to generate self-signed SSL certificate
generate_self_signed_cert() {
    print_status "Generating self-signed SSL certificate..."
    
    # Create SSL directory
    mkdir -p "$SSL_DIR/private"
    mkdir -p "$SSL_DIR/certs"
    
    # Generate private key
    openssl genrsa -out "$SSL_DIR/private/dns-update.key" 2048
    
    # Generate certificate signing request
    openssl req -new -key "$SSL_DIR/private/dns-update.key" \
        -out /tmp/dns-update.csr \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN_NAME"
    
    # Generate self-signed certificate
    openssl x509 -req -days 365 -in /tmp/dns-update.csr \
        -signkey "$SSL_DIR/private/dns-update.key" \
        -out "$SSL_DIR/certs/dns-update.crt"
    
    # Set proper permissions
    chmod 600 "$SSL_DIR/private/dns-update.key"
    chmod 644 "$SSL_DIR/certs/dns-update.crt"
    
    # Clean up
    rm /tmp/dns-update.csr
    
    print_status "Self-signed SSL certificate generated"
}

# Function to configure HTTP-only mode
configure_http_only() {
    print_status "Configuring HTTP-only mode..."
    
    # Use HTTP-only configuration
    cp nginx/dns-update-http.conf "$SITES_AVAILABLE/dns-update"
    
    # Replace domain placeholder
    sed -i "s/your-domain.com/$DOMAIN_NAME/g" "$SITES_AVAILABLE/dns-update"
    
    # Test nginx configuration
    if nginx -t; then
        print_status "Nginx HTTP-only configuration is valid"
        systemctl reload nginx
    else
        print_error "Nginx configuration is invalid"
        exit 1
    fi
    
    print_status "HTTP-only mode configured successfully"
    print_warning "Note: HTTP-only mode is not recommended for production use"
}

# Function to obtain Let's Encrypt certificate
obtain_lets_encrypt_cert() {
    print_status "Obtaining Let's Encrypt SSL certificate..."
    
    # Temporarily modify nginx config for certbot
    cp "$SITES_AVAILABLE/dns-update" "$SITES_AVAILABLE/dns-update.temp"
    
    # Create HTTP-only config for certbot
    cat > "$SITES_AVAILABLE/dns-update" << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    # Reload nginx
    systemctl reload nginx
    
    # Obtain certificate
    if certbot --nginx -d "$DOMAIN_NAME" --email "$CERT_EMAIL" --agree-tos --non-interactive; then
        print_status "Let's Encrypt certificate obtained successfully"
        
        # Restore original config
        mv "$SITES_AVAILABLE/dns-update.temp" "$SITES_AVAILABLE/dns-update"
        systemctl reload nginx
    else
        print_error "Failed to obtain Let's Encrypt certificate"
        print_warning "Falling back to self-signed certificate"
        
        # Restore original config
        mv "$SITES_AVAILABLE/dns-update.temp" "$SITES_AVAILABLE/dns-update"
        generate_self_signed_cert
        systemctl reload nginx
    fi
}

# Function to configure firewall
configure_firewall() {
    print_status "Configuring firewall..."
    
    if command -v ufw > /dev/null 2>&1; then
        # Ubuntu/Debian UFW
        ufw allow 'Nginx Full'
        ufw allow ssh
        print_status "UFW firewall configured"
    elif command -v firewall-cmd > /dev/null 2>&1; then
        # CentOS/RHEL/Fedora firewalld
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --reload
        print_status "Firewalld configured"
    else
        print_warning "No supported firewall found"
    fi
}

# Function to create log rotation
setup_log_rotation() {
    print_status "Setting up log rotation..."
    
    cat > /etc/logrotate.d/dns-update-nginx << EOF
/var/log/nginx/dns-update-*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 nginx nginx
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 \$(cat /var/run/nginx.pid)
        fi
    endscript
}
EOF
    
    print_status "Log rotation configured"
}

# Function to show final instructions
    show_final_instructions() {
        print_header "Installation Complete!"
        echo "================================"
        echo ""
        echo -e "${GREEN}Nginx reverse proxy has been installed and configured.${NC}"
        echo ""
        echo "Configuration:"
        echo "  - Domain: $DOMAIN_NAME"
        
        # Determine SSL mode
        if [ -f "$SITES_AVAILABLE/dns-update" ] && grep -q "ssl_certificate" "$SITES_AVAILABLE/dns-update"; then
            if [ -f "$SSL_DIR/certs/dns-update.crt" ]; then
                SSL_MODE="Self-signed SSL"
                TEST_URL="https://$DOMAIN_NAME"
            else
                SSL_MODE="Let's Encrypt SSL"
                TEST_URL="https://$DOMAIN_NAME"
            fi
        else
            SSL_MODE="HTTP only"
            TEST_URL="http://$DOMAIN_NAME"
        fi
        
        echo "  - SSL Mode: $SSL_MODE"
        echo "  - Nginx Config: $SITES_AVAILABLE/dns-update"
        echo "  - Logs: /var/log/nginx/dns-update-*.log"
        echo ""
        echo "Service Management:"
        echo "  - Start nginx: sudo systemctl start nginx"
        echo "  - Stop nginx: sudo systemctl stop nginx"
        echo "  - Reload nginx: sudo systemctl reload nginx"
        echo "  - Check status: sudo systemctl status nginx"
        echo ""
        echo "Testing:"
        echo "  - Health check: curl $TEST_URL/health"
        echo "  - DNS update: curl -X POST $TEST_URL/update-dns -H 'Content-Type: text/plain' -d '192.168.1.100'"
        echo ""
        echo -e "${YELLOW}Important:${NC}"
        echo "1. Ensure your DNS service is running on port 5000"
        echo "2. Update your domain's DNS A record to point to this server"
        if [ "$SSL_MODE" != "HTTP only" ]; then
            echo "3. Consider setting up automatic SSL certificate renewal"
        else
            echo "3. HTTP-only mode is not recommended for production use"
        fi
        echo ""
    }

# Main installation function
main() {
    print_header "Nginx Reverse Proxy Installation"
    echo "====================================="
    
    # Check if running as root
    check_root
    
    # Get user input
    get_domain_name
    get_email
    
    # Install nginx
    install_nginx
    
    # Configure nginx
    configure_nginx
    
    # Choose SSL certificate type
    echo ""
    echo "SSL Certificate Options:"
    echo "1. Let's Encrypt (recommended, requires public domain)"
    echo "2. Self-signed (for testing/internal use)"
    echo "3. HTTP only (no SSL, for internal networks)"
    read -p "Choose SSL certificate type (1, 2, or 3): " ssl_choice
    
    case $ssl_choice in
        1)
            obtain_lets_encrypt_cert
            ;;
        2)
            generate_self_signed_cert
            ;;
        3)
            configure_http_only
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    # Configure firewall
    configure_firewall
    
    # Setup log rotation
    setup_log_rotation
    
    # Enable and start nginx
    systemctl enable nginx
    systemctl start nginx
    
    # Show final instructions
    show_final_instructions
}

# Run main function
main 