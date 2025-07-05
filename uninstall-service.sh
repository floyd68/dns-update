#!/bin/bash

# DNS Update Service Uninstallation Script
# This script removes the DNS Update Service systemd service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="dns-update"
SERVICE_USER="dns-updater"
SERVICE_GROUP="dns-updater"
INSTALL_DIR="/opt/dns-update"
SERVICE_FILE="/etc/systemd/system/dns-update.service"
ENV_FILE="/etc/dns-update/env"

echo -e "${YELLOW}DNS Update Service Uninstallation${NC}"
echo "====================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

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

# Stop and disable the service
print_status "Stopping and disabling service..."
if systemctl is-active --quiet dns-update; then
    systemctl stop dns-update
    print_status "Stopped dns-update service"
else
    print_warning "Service was not running"
fi

if systemctl is-enabled --quiet dns-update; then
    systemctl disable dns-update
    print_status "Disabled dns-update service"
else
    print_warning "Service was not enabled"
fi

# Remove systemd service file
print_status "Removing systemd service file..."
if [ -f "$SERVICE_FILE" ]; then
    rm -f "$SERVICE_FILE"
    print_status "Removed service file: $SERVICE_FILE"
else
    print_warning "Service file not found: $SERVICE_FILE"
fi

# Reload systemd
print_status "Reloading systemd..."
systemctl daemon-reload

# Remove installation directory
print_status "Removing installation directory..."
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    print_status "Removed installation directory: $INSTALL_DIR"
else
    print_warning "Installation directory not found: $INSTALL_DIR"
fi

# Remove environment configuration
print_status "Removing environment configuration..."
if [ -f "$ENV_FILE" ]; then
    rm -f "$ENV_FILE"
    print_status "Removed environment file: $ENV_FILE"
else
    print_warning "Environment file not found: $ENV_FILE"
fi

# Remove configuration directory if empty
if [ -d "/etc/dns-update" ] && [ -z "$(ls -A /etc/dns-update)" ]; then
    rmdir /etc/dns-update
    print_status "Removed empty configuration directory: /etc/dns-update"
fi

# Remove service user and group
print_status "Removing service user and group..."
if getent passwd $SERVICE_USER > /dev/null 2>&1; then
    userdel $SERVICE_USER
    print_status "Removed user: $SERVICE_USER"
else
    print_warning "User $SERVICE_USER not found"
fi

if getent group $SERVICE_GROUP > /dev/null 2>&1; then
    groupdel $SERVICE_GROUP
    print_status "Removed group: $SERVICE_GROUP"
else
    print_warning "Group $SERVICE_GROUP not found"
fi

print_status "Uninstallation completed successfully!"
echo ""
echo -e "${GREEN}All DNS Update Service files and configurations have been removed.${NC}" 