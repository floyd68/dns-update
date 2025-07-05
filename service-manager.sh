#!/bin/bash

# DNS Update Service Manager
# This script provides easy management commands for the DNS Update Service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service name
SERVICE_NAME="dns-update"

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

# Function to check if service exists
check_service_exists() {
    if ! systemctl list-unit-files | grep -q "^dns-update.service"; then
        print_error "DNS Update Service is not installed"
        echo "Run: sudo ./install-service.sh"
        exit 1
    fi
}

# Function to show service status
show_status() {
    print_header "DNS Update Service Status"
    echo "================================"
    
    # Check if service is installed
    if systemctl list-unit-files | grep -q "^dns-update.service"; then
        print_status "Service is installed"
    else
        print_error "Service is not installed"
        return 1
    fi
    
    # Check if service is enabled
    if systemctl is-enabled --quiet dns-update; then
        print_status "Service is enabled (will start on boot)"
    else
        print_warning "Service is not enabled"
    fi
    
    # Check if service is running
    if systemctl is-active --quiet dns-update; then
        print_status "Service is running"
    else
        print_warning "Service is not running"
    fi
    
    # Show recent logs
    echo ""
    print_header "Recent Logs (last 10 lines):"
    echo "================================"
    journalctl -u dns-update --no-pager -n 10
}

# Function to start service
start_service() {
    print_header "Starting DNS Update Service"
    echo "================================"
    
    check_service_exists
    
    if systemctl is-active --quiet dns-update; then
        print_warning "Service is already running"
    else
        print_status "Starting service..."
        systemctl start dns-update
        sleep 2
        
        if systemctl is-active --quiet dns-update; then
            print_status "Service started successfully"
        else
            print_error "Failed to start service"
            echo "Check logs with: sudo journalctl -u dns-update -f"
            exit 1
        fi
    fi
}

# Function to stop service
stop_service() {
    print_header "Stopping DNS Update Service"
    echo "================================"
    
    check_service_exists
    
    if ! systemctl is-active --quiet dns-update; then
        print_warning "Service is not running"
    else
        print_status "Stopping service..."
        systemctl stop dns-update
        print_status "Service stopped"
    fi
}

# Function to restart service
restart_service() {
    print_header "Restarting DNS Update Service"
    echo "================================"
    
    check_service_exists
    
    print_status "Restarting service..."
    systemctl restart dns-update
    sleep 2
    
    if systemctl is-active --quiet dns-update; then
        print_status "Service restarted successfully"
    else
        print_error "Failed to restart service"
        echo "Check logs with: sudo journalctl -u dns-update -f"
        exit 1
    fi
}

# Function to enable service
enable_service() {
    print_header "Enabling DNS Update Service"
    echo "================================"
    
    check_service_exists
    
    if systemctl is-enabled --quiet dns-update; then
        print_warning "Service is already enabled"
    else
        print_status "Enabling service..."
        systemctl enable dns-update
        print_status "Service enabled (will start on boot)"
    fi
}

# Function to disable service
disable_service() {
    print_header "Disabling DNS Update Service"
    echo "================================"
    
    check_service_exists
    
    if ! systemctl is-enabled --quiet dns-update; then
        print_warning "Service is not enabled"
    else
        print_status "Disabling service..."
        systemctl disable dns-update
        print_status "Service disabled (will not start on boot)"
    fi
}

# Function to show logs
show_logs() {
    print_header "DNS Update Service Logs"
    echo "================================"
    
    check_service_exists
    
    if [ "$1" = "follow" ]; then
        print_status "Showing logs (following)..."
        journalctl -u dns-update -f
    else
        print_status "Showing recent logs..."
        journalctl -u dns-update --no-pager -n 50
    fi
}

# Function to test service
test_service() {
    print_header "Testing DNS Update Service"
    echo "================================"
    
    check_service_exists
    
    if ! systemctl is-active --quiet dns-update; then
        print_error "Service is not running"
        echo "Start the service first: sudo systemctl start dns-update"
        exit 1
    fi
    
    print_status "Testing health endpoint..."
    if command -v curl > /dev/null 2>&1; then
        response=$(curl -s -w "%{http_code}" http://localhost:5000/health)
        http_code="${response: -3}"
        body="${response%???}"
        
        if [ "$http_code" = "200" ]; then
            print_status "Health check passed"
            echo "Response: $body"
        else
            print_error "Health check failed (HTTP $http_code)"
            echo "Response: $body"
        fi
    else
        print_warning "curl not available, skipping health check"
    fi
    
    print_status "Service test completed"
}

# Function to show configuration
show_config() {
    print_header "DNS Update Service Configuration"
    echo "====================================="
    
    print_status "Service file: /etc/systemd/system/dns-update.service"
    print_status "Installation directory: /opt/dns-update"
    print_status "Environment file: /etc/dns-update/env"
    print_status "Service user: dns-updater"
    
    echo ""
    print_header "Environment Configuration:"
    echo "================================"
    if [ -f "/etc/dns-update/env" ]; then
        cat /etc/dns-update/env
    else
        print_warning "Environment file not found"
    fi
}

# Function to show help
show_help() {
    print_header "DNS Update Service Manager"
    echo "================================"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  status     - Show service status and recent logs"
    echo "  start      - Start the service"
    echo "  stop       - Stop the service"
    echo "  restart    - Restart the service"
    echo "  enable     - Enable service to start on boot"
    echo "  disable    - Disable service from starting on boot"
    echo "  logs       - Show recent logs"
    echo "  logs-follow- Show logs and follow new entries"
    echo "  test       - Test the service (health check)"
    echo "  config     - Show configuration information"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 start"
    echo "  $0 logs-follow"
    echo ""
}

# Main script logic
case "${1:-help}" in
    status)
        show_status
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    enable)
        enable_service
        ;;
    disable)
        disable_service
        ;;
    logs)
        show_logs
        ;;
    logs-follow)
        show_logs follow
        ;;
    test)
        test_service
        ;;
    config)
        show_config
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