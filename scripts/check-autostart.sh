#!/bin/bash

# Path Payment Terminal API Emulator - Check Auto-Start Configuration
# This script verifies that services are enabled to start on boot

echo "========================================="
echo "Checking Auto-Start Configuration"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo"
    exit 1
fi

echo ""
echo "Checking path-terminal-api service..."
if systemctl is-enabled path-terminal-api >/dev/null 2>&1; then
    echo "✓ path-terminal-api is ENABLED (will start on boot)"
else
    echo "✗ path-terminal-api is NOT enabled"
    echo "  Enabling now..."
    systemctl enable path-terminal-api
    echo "  ✓ Enabled"
fi

echo ""
echo "Checking nginx service..."
if systemctl is-enabled nginx >/dev/null 2>&1; then
    echo "✓ nginx is ENABLED (will start on boot)"
else
    echo "✗ nginx is NOT enabled"
    echo "  Enabling now..."
    systemctl enable nginx
    echo "  ✓ Enabled"
fi

echo ""
echo "========================================="
echo "Service Status"
echo "========================================="
echo ""
systemctl status path-terminal-api --no-pager -l | head -10
echo ""
echo "To verify auto-start is configured:"
echo "  systemctl is-enabled path-terminal-api"
echo "  systemctl is-enabled nginx"
echo ""
echo "Both should return 'enabled'"

