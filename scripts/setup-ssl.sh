#!/bin/bash

# Path Payment Terminal API Emulator - SSL/HTTPS Setup Script
# This script sets up Let's Encrypt SSL certificate for your domain

set -e

DOMAIN="${1:-}"

if [ -z "$DOMAIN" ]; then
    echo "Usage: sudo ./setup-ssl.sh <domain>"
    echo "Example: sudo ./setup-ssl.sh posapi.path2ai.tech"
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

# Update Nginx configuration with domain
echo "Updating Nginx configuration..."
sudo tee /etc/nginx/sites-available/path-terminal-api > /dev/null <<EOF
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

# Test Nginx configuration
echo "Testing Nginx configuration..."
sudo nginx -t

# Reload Nginx
echo "Reloading Nginx..."
sudo systemctl reload nginx

# Install Certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# Obtain SSL certificate
echo "Obtaining SSL certificate from Let's Encrypt..."
echo "This will prompt for your email address and agreement to terms."
echo ""

sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@path2ai.tech --redirect

# Verify certificate
echo ""
echo "========================================="
echo "SSL Setup Complete!"
echo "========================================="
echo ""
echo "Certificate obtained for: $DOMAIN"
echo ""
echo "Test your site: https://$DOMAIN"
echo ""
echo "Certificate will auto-renew. Test renewal with:"
echo "  sudo certbot renew --dry-run"
echo ""

