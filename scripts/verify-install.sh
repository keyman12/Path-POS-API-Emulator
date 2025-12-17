#!/bin/bash

# Path Payment Terminal API Emulator - Installation Verification Script
# This script verifies the installation and fixes common issues

set -e

APP_DIR="/opt/path-terminal-api"
BACKEND_DIR="$APP_DIR/backend"

echo "========================================="
echo "Path Terminal API - Installation Verification"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS="amzn"
fi

# Determine Python command
if [[ "$OS" == "amzn" ]] || [[ "$OS" == "amazon" ]]; then
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    else
        PYTHON_CMD="python3"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Detected OS: $OS"
echo "Using Python: $PYTHON_CMD"
echo ""

# Check if directory exists
if [ ! -d "$APP_DIR" ]; then
    echo "ERROR: Application directory not found: $APP_DIR"
    echo "Please run deploy.sh first"
    exit 1
fi

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo "ERROR: Backend directory not found: $BACKEND_DIR"
    exit 1
fi

# Check if venv exists
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "Virtual environment not found. Creating..."
    cd "$BACKEND_DIR"
    $PYTHON_CMD -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment exists."
fi

# Activate venv and install/upgrade dependencies
echo "Installing/upgrading dependencies..."
cd "$BACKEND_DIR"
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip --quiet

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "Dependencies installed."
else
    echo "ERROR: requirements.txt not found in $BACKEND_DIR"
    exit 1
fi

# Verify uvicorn is installed
if [ -f "venv/bin/uvicorn" ]; then
    echo "✓ uvicorn found at: venv/bin/uvicorn"
else
    echo "ERROR: uvicorn not found in virtual environment"
    echo "Attempting to install uvicorn..."
    pip install uvicorn[standard]
    if [ -f "venv/bin/uvicorn" ]; then
        echo "✓ uvicorn installed successfully"
    else
        echo "ERROR: Failed to install uvicorn"
        exit 1
    fi
fi

# Check file permissions
echo "Checking permissions..."
chown -R ec2-user:ec2-user "$APP_DIR" 2>/dev/null || chown -R ubuntu:ubuntu "$APP_DIR" 2>/dev/null

# Verify systemd service file
if [ -f "/etc/systemd/system/path-terminal-api.service" ]; then
    echo "✓ Systemd service file exists"
    
    # Check if ExecStart path is correct
    if grep -q "$APP_DIR/backend/venv/bin/uvicorn" /etc/systemd/system/path-terminal-api.service; then
        echo "✓ Service file ExecStart path is correct"
    else
        echo "WARNING: Service file ExecStart path may be incorrect"
    fi
else
    echo "WARNING: Systemd service file not found"
fi

echo ""
echo "========================================="
echo "Verification Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Reload systemd: sudo systemctl daemon-reload"
echo "2. Start service: sudo systemctl start path-terminal-api"
echo "3. Check status: sudo systemctl status path-terminal-api"
echo "4. View logs: sudo journalctl -u path-terminal-api -f"
echo ""

