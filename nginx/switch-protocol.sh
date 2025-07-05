#!/bin/bash

# Nginx Protocol Switch Script
# This script allows switching between HTTP and HTTPS modes

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

# Function to check current mode
check_current_mode() {
    if [ -f "$SITES_AVAILABLE/dns-update" ]; then
        if grep -q "ssl_certificate" "$SITES_AVAILABLE/dns-update"; then
            echo "https"
        else
            echo "http"
        fi
    else
        echo "not_configured"
    fi
}

# Function to switch to HTTP mode
switch_to_http() {
    print_status "Switching to HTTP mode..."
    
    # Backup current configuration
    if [ -f "$SITES_AVAILABLE/dns-update" ]; then
        cp "$SITES_AVAILABLE/dns-update" "$SITES_AVAILABLE/dns-update.backup"
        print_status "Backed up current configuration"
    fi
    
    # Get domain name from current config or user input
    DOMAIN_NAME=$(grep "server_name" "$SITES_AVAILABLE/dns-update" | head -1 | awk '{print $2}' | sed 's/;//')
    
    if [ -z "$DOMAIN_NAME" ]; then
        read -p "Enter your domain name: " DOMAIN_NAME
    fi
    
    # Copy HTTP configuration
    cp nginx/dns-update-http.conf "$SITES_AVAILABLE/dns-update"
    
    # Replace domain placeholder
    sed -i "s/your-domain.com/$DOMAIN_NAME/g" "$SITES_AVAILABLE/dns-update"
    
    # Test and reload nginx
    if nginx -t; then
        systemctl reload nginx
        print_status "Successfully switched to HTTP mode"
        print_warning "HTTP mode is not recommended for production use"
    else
        print_error "Nginx configuration is invalid"
        # Restore backup
        if [ -f "$SITES_AVAILABLE/dns-update.backup" ]; then
            mv "$SITES_AVAILABLE/dns-update.backup" "$SITES_AVAILABLE/dns-update"
            systemctl reload nginx
        fi
        exit 1
    fi
}

# Function to switch to HTTPS mode
switch_to_https() {
    print_status "Switching to HTTPS mode..."
    
    # Backup current configuration
    if [ -f "$SITES_AVAILABLE/dns-update" ]; then
        cp "$SITES_AVAILABLE/dns-update" "$SITES_AVAILABLE/dns-update.backup"
        print_status "Backed up current configuration"
    fi
    
    # Get domain name from current config or user input
    DOMAIN_NAME=$(grep "server_name" "$SITES_AVAILABLE/dns-update" | head -1 | awk '{print $2}' | sed 's/;//')
    
    if [ -z "$DOMAIN_NAME" ]; then
        read -p "Enter your domain name: " DOMAIN_NAME
    fi
    
    # Copy HTTPS configuration
    cp nginx/dns-update.conf "$SITES_AVAILABLE/dns-update"
    
    # Replace domain placeholder
    sed -i "s/your-domain.com/$DOMAIN_NAME/g" "$SITES_AVAILABLE/dns-update"
    
    # Choose SSL certificate type
    echo ""
    echo "SSL Certificate Options:"
    echo "1. Let's Encrypt (recommended, requires public domain)"
    echo "2. Self-signed (for testing/internal use)"
    read -p "Choose SSL certificate type (1 or 2): " ssl_choice
    
    case $ssl_choice in
        1)
            # Check if certbot is available
            if ! command -v certbot > /dev/null 2>&1; then
                print_error "Certbot is not installed. Please run the full installation script first."
                exit 1
            fi
            
            read -p "Enter your email address for SSL certificate: " CERT_EMAIL
            
            # Temporarily modify config for certbot
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
            ;;
        2)
            generate_self_signed_cert
            systemctl reload nginx
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    print_status "Successfully switched to HTTPS mode"
}

# Function to generate self-signed certificate
generate_self_signed_cert() {
    print_status "Generating self-signed SSL certificate..."
    
    # Create SSL directory
    mkdir -p "$SSL_DIR/private"
    mkdir -p "$SSL_DIR/certs"
    
    # Get domain name
    DOMAIN_NAME=$(grep "server_name" "$SITES_AVAILABLE/dns-update" | head -1 | awk '{print $2}' | sed 's/;//')
    
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

# Function to show current status
show_status() {
    print_header "Current Nginx Configuration Status"
    echo "====================================="
    
    CURRENT_MODE=$(check_current_mode)
    
    case $CURRENT_MODE in
        "https")
            print_status "Current mode: HTTPS (SSL enabled)"
            if [ -f "$SSL_DIR/certs/dns-update.crt" ]; then
                echo "  - SSL Certificate: Self-signed"
            else
                echo "  - SSL Certificate: Let's Encrypt"
            fi
            ;;
        "http")
            print_status "Current mode: HTTP (no SSL)"
            print_warning "HTTP mode is not recommended for production use"
            ;;
        "not_configured")
            print_error "Nginx is not configured for DNS update service"
            echo "Run the installation script first: sudo ./nginx/install-nginx.sh"
            exit 1
            ;;
    esac
    
    # Show domain name
    if [ -f "$SITES_AVAILABLE/dns-update" ]; then
        DOMAIN_NAME=$(grep "server_name" "$SITES_AVAILABLE/dns-update" | head -1 | awk '{print $2}' | sed 's/;//')
        echo "  - Domain: $DOMAIN_NAME"
    fi
    
    # Show nginx status
    if systemctl is-active --quiet nginx; then
        print_status "Nginx service: Running"
    else
        print_warning "Nginx service: Not running"
    fi
}

# Function to show help
show_help() {
    print_header "Nginx Protocol Switch Script"
    echo "================================"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  status     - Show current configuration status"
    echo "  http       - Switch to HTTP mode"
    echo "  https      - Switch to HTTPS mode"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 http"
    echo "  $0 https"
    echo ""
}

# Main script logic
case "${1:-help}" in
    status)
        check_root
        show_status
        ;;
    http)
        check_root
        switch_to_http
        ;;
    https)
        check_root
        switch_to_https
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 