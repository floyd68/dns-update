#!/bin/bash

# DNS Update Service Installation Script
# This script installs the DNS Update Service as a systemd service

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

echo -e "${GREEN}DNS Update Service Installation${NC}"
echo "=================================="

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

# Create service user and group
print_status "Creating service user and group..."
if ! getent group $SERVICE_GROUP > /dev/null 2>&1; then
    groupadd $SERVICE_GROUP
    print_status "Created group: $SERVICE_GROUP"
else
    print_warning "Group $SERVICE_GROUP already exists"
fi

if ! getent passwd $SERVICE_USER > /dev/null 2>&1; then
    useradd -r -s /bin/false -g $SERVICE_GROUP -d $INSTALL_DIR $SERVICE_USER
    print_status "Created user: $SERVICE_USER"
else
    print_warning "User $SERVICE_USER already exists"
fi

# Create installation directory
print_status "Creating installation directory..."
mkdir -p $INSTALL_DIR
mkdir -p $INSTALL_DIR/logs
mkdir -p /etc/dns-update

# Copy application files
print_status "Copying application files..."
cp app.py $INSTALL_DIR/
cp config.py $INSTALL_DIR/
cp requirements.txt $INSTALL_DIR/
cp start.py $INSTALL_DIR/
cp test_dns_update.py $INSTALL_DIR/

# Set proper permissions
chown -R $SERVICE_USER:$SERVICE_GROUP $INSTALL_DIR
chmod 755 $INSTALL_DIR
chmod 644 $INSTALL_DIR/*.py
chmod 644 $INSTALL_DIR/requirements.txt

# Create virtual environment
print_status "Setting up Python virtual environment..."
cd $INSTALL_DIR
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Created virtual environment"
else
    print_warning "Virtual environment already exists"
fi

# Install dependencies
print_status "Installing Python dependencies..."
$INSTALL_DIR/venv/bin/pip install --upgrade pip
$INSTALL_DIR/venv/bin/pip install -r requirements.txt

# Create environment file template
print_status "Creating environment configuration file..."
cat > $ENV_FILE << 'EOF'
# DNS Update Service Environment Configuration
# Required: Set these values for your environment

# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1

# DNS Configuration (REQUIRED)
HOSTED_ZONE_ID=Z1234567890ABC
DOMAIN_NAME=api.example.com

# IP Validation Configuration (Optional)
ENABLE_IP_VALIDATION=true
ALLOWED_IPS=
ALLOWED_SUBNETS=

# Password Authentication Configuration (Optional)
ENABLE_PASSWORD_AUTH=true
AUTH_PASSWORD=your_secure_password_here

# Service Configuration (Optional)
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
DNS_TTL=300
LOG_LEVEL=INFO
EOF

# Set proper permissions for environment file
chown $SERVICE_USER:$SERVICE_GROUP $ENV_FILE
chmod 600 $ENV_FILE

# Install systemd service file
print_status "Installing systemd service..."
cp dns-update.service $SERVICE_FILE

# Reload systemd and enable service
print_status "Reloading systemd and enabling service..."
systemctl daemon-reload
systemctl enable dns-update.service

print_status "Installation completed successfully!"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit the environment file: sudo nano $ENV_FILE"
echo "2. Set your AWS credentials and DNS configuration"
echo "3. Start the service: sudo systemctl start dns-update"
echo "4. Check status: sudo systemctl status dns-update"
echo "5. View logs: sudo journalctl -u dns-update -f"
echo ""
echo -e "${YELLOW}Service commands:${NC}"
echo "  Start:   sudo systemctl start dns-update"
echo "  Stop:    sudo systemctl stop dns-update"
echo "  Restart: sudo systemctl restart dns-update"
echo "  Status:  sudo systemctl status dns-update"
echo "  Logs:    sudo journalctl -u dns-update -f"
echo ""
echo -e "${GREEN}Service will start automatically on boot${NC}" 