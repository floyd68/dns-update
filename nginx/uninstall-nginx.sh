#!/bin/bash

# Nginx Reverse Proxy Uninstallation Script for DNS Update Service
# This script removes nginx configuration and SSL certificates

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

# Function to remove nginx configuration
remove_nginx_config() {
    print_status "Removing nginx configuration..."
    
    # Remove site configuration
    if [ -f "$SITES_AVAILABLE/dns-update" ]; then
        rm -f "$SITES_AVAILABLE/dns-update"
        print_status "Removed nginx site configuration"
    else
        print_warning "Nginx site configuration not found"
    fi
    
    # Remove symlink
    if [ -L "$SITES_ENABLED/dns-update" ]; then
        rm -f "$SITES_ENABLED/dns-update"
        print_status "Removed nginx site symlink"
    else
        print_warning "Nginx site symlink not found"
    fi
    
    # Test nginx configuration
    if nginx -t; then
        print_status "Nginx configuration is valid"
        systemctl reload nginx
    else
        print_error "Nginx configuration is invalid"
        print_warning "You may need to manually fix nginx configuration"
    fi
}

# Function to remove SSL certificates
remove_ssl_certs() {
    print_status "Removing SSL certificates..."
    
    # Remove self-signed certificates
    if [ -f "$SSL_DIR/private/dns-update.key" ]; then
        rm -f "$SSL_DIR/private/dns-update.key"
        print_status "Removed SSL private key"
    fi
    
    if [ -f "$SSL_DIR/certs/dns-update.crt" ]; then
        rm -f "$SSL_DIR/certs/dns-update.crt"
        print_status "Removed SSL certificate"
    fi
    
    # Remove Let's Encrypt certificates if they exist
    if [ -d "/etc/letsencrypt/live" ]; then
        print_warning "Let's Encrypt certificates may still exist"
        print_warning "To remove them, run: certbot delete --cert-name your-domain.com"
    fi
}

# Function to remove log rotation
remove_log_rotation() {
    print_status "Removing log rotation configuration..."
    
    if [ -f "/etc/logrotate.d/dns-update-nginx" ]; then
        rm -f "/etc/logrotate.d/dns-update-nginx"
        print_status "Removed log rotation configuration"
    else
        print_warning "Log rotation configuration not found"
    fi
}

# Function to remove nginx logs
remove_nginx_logs() {
    print_status "Removing nginx logs..."
    
    # Remove DNS update specific logs
    for log_file in /var/log/nginx/dns-update-*.log; do
        if [ -f "$log_file" ]; then
            rm -f "$log_file"
            print_status "Removed log file: $log_file"
        fi
    done
    
    # Rotate nginx logs to clean them
    if [ -f /var/run/nginx.pid ]; then
        nginx -s reload
        print_status "Reloaded nginx to clean logs"
    fi
}

# Function to uninstall nginx (optional)
uninstall_nginx() {
    echo ""
    read -p "Do you want to completely uninstall nginx? (y/N): " remove_nginx
    
    if [[ $remove_nginx =~ ^[Yy]$ ]]; then
        print_status "Uninstalling nginx..."
        
        if command -v apt-get > /dev/null 2>&1; then
            # Debian/Ubuntu
            apt-get remove --purge -y nginx nginx-common
            apt-get autoremove -y
        elif command -v yum > /dev/null 2>&1; then
            # CentOS/RHEL
            yum remove -y nginx
        elif command -v dnf > /dev/null 2>&1; then
            # Fedora
            dnf remove -y nginx
        fi
        
        # Remove nginx directories
        rm -rf /etc/nginx
        rm -rf /var/log/nginx
        rm -rf /var/cache/nginx
        
        print_status "Nginx completely uninstalled"
    else
        print_status "Nginx will remain installed"
    fi
}

# Function to show final status
show_final_status() {
    print_header "Uninstallation Complete!"
    echo "================================"
    echo ""
    echo -e "${GREEN}Nginx reverse proxy configuration has been removed.${NC}"
    echo ""
    echo "Removed:"
    echo "  - Nginx site configuration"
    echo "  - SSL certificates"
    echo "  - Log rotation configuration"
    echo "  - DNS update specific logs"
    echo ""
    echo -e "${YELLOW}Note:${NC}"
    echo "- Nginx service may still be running"
    echo "- Let's Encrypt certificates may need manual cleanup"
    echo "- Firewall rules may need manual adjustment"
    echo ""
}

# Main uninstallation function
main() {
    print_header "Nginx Reverse Proxy Uninstallation"
    echo "======================================="
    
    # Check if running as root
    check_root
    
    # Confirm uninstallation
    echo ""
    echo -e "${YELLOW}This will remove the nginx reverse proxy configuration for DNS Update Service.${NC}"
    read -p "Are you sure you want to continue? (y/N): " confirm
    
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_status "Uninstallation cancelled"
        exit 0
    fi
    
    # Remove nginx configuration
    remove_nginx_config
    
    # Remove SSL certificates
    remove_ssl_certs
    
    # Remove log rotation
    remove_log_rotation
    
    # Remove nginx logs
    remove_nginx_logs
    
    # Optionally uninstall nginx
    uninstall_nginx
    
    # Show final status
    show_final_status
}

# Run main function
main 