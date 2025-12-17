#!/bin/bash

# Path Payment Terminal API Emulator - Initial Deployment Script
# Run this script on a fresh EC2 instance to set up the application
# Supports Amazon Linux 2023

set -e

APP_DIR="/opt/path-terminal-api"
REPO_URL="${1:-}"  # Pass repository URL as first argument

echo "========================================="
echo "Path Terminal API - Deployment Script"
echo "========================================="

if [ -z "$REPO_URL" ]; then
    echo "Usage: sudo ./deploy.sh <repository-url>"
    echo "Example: sudo ./deploy.sh https://github.com/your-org/path-terminal-api.git"
    exit 1
fi

# Detect OS and set variables
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS. Assuming Amazon Linux."
    OS="amzn"
fi

# Determine package manager and user
if [[ "$OS" == "amzn" ]] || [[ "$OS" == "amazon" ]]; then
    PKG_MGR="dnf"
    SERVICE_USER="ec2-user"
    echo "Detected: Amazon Linux"
elif [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
    PKG_MGR="apt"
    SERVICE_USER="ubuntu"
    echo "Detected: Ubuntu/Debian"
else
    echo "Warning: Unknown OS. Assuming Amazon Linux defaults."
    PKG_MGR="dnf"
    SERVICE_USER="ec2-user"
fi

# Update system
echo "Updating system packages..."
if [[ "$PKG_MGR" == "dnf" ]]; then
    sudo dnf update -y
    sudo dnf install -y python3 python3-pip python3.11 python3.11-pip nginx git
    # Ensure python3.11 is available, fallback to python3
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    else
        PYTHON_CMD="python3"
    fi
else
    sudo apt update
    sudo apt upgrade -y
    sudo apt install -y python3-pip python3-venv nginx git
    PYTHON_CMD="python3"
fi

# Clone repository
echo "Cloning repository..."
if [ -d "$APP_DIR" ]; then
    echo "Directory exists, removing..."
    sudo rm -rf "$APP_DIR"
fi

sudo git clone "$REPO_URL" "$APP_DIR"
sudo chown -R $SERVICE_USER:$SERVICE_USER "$APP_DIR"

# Create virtual environment
echo "Setting up Python virtual environment..."
cd "$APP_DIR/backend"
$PYTHON_CMD -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/path-terminal-api.service > /dev/null <<EOF
[Unit]
Description=Path Payment Terminal API Emulator
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$APP_DIR/backend
Environment="PATH=$APP_DIR/backend/venv/bin"
Environment="ACK_ONLY=false"
Environment="RESPONSE_DELAY_MS=500"
Environment="SESSION_TIMEOUT_MINUTES=30"
Environment="PORT=8000"
ExecStart=$APP_DIR/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo "Configuring Nginx..."
if [[ "$PKG_MGR" == "dnf" ]]; then
    # Amazon Linux - Nginx config location
    sudo tee /etc/nginx/conf.d/path-terminal-api.conf > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF
else
    # Ubuntu/Debian - Nginx config location
    sudo tee /etc/nginx/sites-available/path-terminal-api > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF
    sudo ln -sf /etc/nginx/sites-available/path-terminal-api /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
fi

# Test Nginx configuration
sudo nginx -t

# Configure firewall (Amazon Linux uses security groups, but enable firewalld if needed)
echo "Configuring firewall..."
if command -v firewall-cmd &> /dev/null; then
    # firewalld (Amazon Linux 2023)
    sudo systemctl enable firewalld
    sudo systemctl start firewalld
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --permanent --add-service=ssh
    sudo firewall-cmd --reload
elif command -v ufw &> /dev/null; then
    # UFW (Ubuntu)
    sudo ufw allow 22/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
else
    echo "Note: Firewall configuration skipped. Ensure AWS Security Group allows ports 22, 80, 443"
fi

# Start services
echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable path-terminal-api
sudo systemctl start path-terminal-api
sudo systemctl enable nginx
sudo systemctl restart nginx

# Check status
sleep 2
echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Service status:"
sudo systemctl status path-terminal-api --no-pager -l
echo ""
echo "Application should be available at: http://$(curl -s ifconfig.me)"
echo ""
echo "To view logs: sudo journalctl -u path-terminal-api -f"
echo "To update: cd $APP_DIR && sudo ./scripts/update.sh"
