#!/bin/bash

# Path Payment Terminal API Emulator - Update Script
# This script updates the application from Git and restarts the service

set -e

APP_DIR="/opt/path-terminal-api"
BACKEND_DIR="$APP_DIR/backend"
SERVICE_NAME="path-terminal-api"

echo "========================================="
echo "Path Terminal API - Update Script"
echo "========================================="

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo"
    exit 1
fi

# Navigate to application directory
cd "$APP_DIR" || exit 1

# Backup current version
echo "Creating backup..."
BACKUP_DIR="$APP_DIR-backup-$(date +%Y%m%d-%H%M%S)"
sudo cp -r "$APP_DIR" "$BACKUP_DIR"
echo "Backup created at: $BACKUP_DIR"

# Stop the service
echo "Stopping service..."
sudo systemctl stop "$SERVICE_NAME" || true

# Pull latest changes
echo "Pulling latest changes from Git..."
cd "$APP_DIR"
git pull origin main || {
    echo "Git pull failed. Restoring from backup..."
    sudo systemctl start "$SERVICE_NAME"
    exit 1
}

# Update Python dependencies
echo "Updating Python dependencies..."
cd "$BACKEND_DIR"
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart the service
echo "Restarting service..."
sudo systemctl start "$SERVICE_NAME"

# Wait a moment and check status
sleep 2
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "✓ Service started successfully"
    echo "✓ Update complete!"
    echo ""
    echo "Service status:"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
else
    echo "✗ Service failed to start!"
    echo "Check logs with: sudo journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

