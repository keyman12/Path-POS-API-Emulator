#!/bin/bash

# Path Payment Terminal API Emulator - SSL/HTTPS Setup Script
# This script sets up Let's Encrypt SSL certificate for your domain
# Supports Amazon Linux 2023 and Ubuntu

set -e

DOMAIN="${1:-}"
EMAIL="${2:-}"

if [ -z "$DOMAIN" ]; then
    echo "Usage: sudo ./setup-ssl.sh <domain> [email]"
    echo "Example: sudo ./setup-ssl.sh posapi.path2ai.tech admin@path2ai.tech"
    echo ""
    echo "If email is not provided, you will be prompted to enter it."
    exit 1
fi

echo "========================================="
echo "SSL/HTTPS Setup for $DOMAIN"
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

# Prompt for email if not provided
if [ -z "$EMAIL" ]; then
    echo ""
    read -p "Enter your email address for Let's Encrypt notifications: " EMAIL
    if [ -z "$EMAIL" ]; then
        echo "Error: Email address is required"
        exit 1
    fi
fi

# Update Nginx configuration with domain
echo "Updating Nginx configuration..."

if [[ "$OS" == "amzn" ]] || [[ "$OS" == "amazon" ]]; then
    # Amazon Linux - use conf.d
    CONFIG_FILE="/etc/nginx/conf.d/path-terminal-api.conf"
    tee "$CONFIG_FILE" > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF
else
    # Ubuntu/Debian - use sites-available
    CONFIG_FILE="/etc/nginx/sites-available/path-terminal-api"
    tee "$CONFIG_FILE" > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF
    ln -sf "$CONFIG_FILE" /etc/nginx/sites-enabled/path-terminal-api
fi

# Test Nginx configuration
echo "Testing Nginx configuration..."
nginx -t

# Reload Nginx
echo "Reloading Nginx..."
systemctl reload nginx

# Install Certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    if [[ "$OS" == "amzn" ]] || [[ "$OS" == "amazon" ]]; then
        dnf update -y
        dnf install -y certbot python3-certbot-nginx
    else
        apt update
        apt install -y certbot python3-certbot-nginx
    fi
fi

# Obtain SSL certificate
echo "Obtaining SSL certificate from Let's Encrypt..."
echo "Using email: $EMAIL"
echo ""

certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "$EMAIL" --redirect

# Verify certificate
echo ""
echo "========================================="
echo "SSL Setup Complete!"
echo "========================================="
echo ""
echo "Certificate obtained for: $DOMAIN"
echo "Certificate email: $EMAIL"
echo ""
echo "Test your site: https://$DOMAIN"
echo ""
echo "Certificate will auto-renew. Test renewal with:"
echo "  certbot renew --dry-run"
echo ""

