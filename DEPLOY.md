# EC2 Deployment Guide

This guide covers deploying the Path Payment Terminal API Emulator to an AWS EC2 instance.

## Prerequisites

- AWS EC2 instance (Amazon Linux 2023 recommended)
- SSH access to the instance
- Python 3.10+ installed
- Git installed

## Initial Setup

### 1. Connect to EC2 Instance

```bash
# Amazon Linux
ssh -i your-key.pem ec2-user@your-ec2-ip

# Ubuntu (if using)
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2. Install System Dependencies

**Amazon Linux 2023:**
```bash
sudo dnf update -y
sudo dnf install -y python3 python3-pip python3.11 python3.11-pip nginx git
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx git
```

### 3. Clone Repository

```bash
cd /opt
sudo git clone <your-repository-url> path-terminal-api
# Amazon Linux
sudo chown -R ec2-user:ec2-user path-terminal-api
# Ubuntu
# sudo chown -R ubuntu:ubuntu path-terminal-api
cd path-terminal-api
```

### 4. Create Virtual Environment

**Amazon Linux 2023:**
```bash
cd backend

# Create virtual environment (use python3.11 if available)
python3.11 -m venv venv || python3 -m venv venv

# Activate and install
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Verify uvicorn is installed
which uvicorn
# Should show: /opt/path-terminal-api/backend/venv/bin/uvicorn
```

**Ubuntu:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Verify uvicorn is installed
which uvicorn
```

### 5. Create Systemd Service

Create `/etc/systemd/system/path-terminal-api.service`:

**Amazon Linux:**
```ini
[Unit]
Description=Path Payment Terminal API Emulator
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/path-terminal-api/backend
Environment="PATH=/opt/path-terminal-api/backend/venv/bin"
Environment="ACK_ONLY=false"
Environment="RESPONSE_DELAY_MS=500"
Environment="SESSION_TIMEOUT_MINUTES=30"
Environment="PORT=8000"
ExecStart=/opt/path-terminal-api/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Ubuntu:** (Change `User=ec2-user` to `User=ubuntu`)

### 6. Configure Nginx

**Amazon Linux 2023:**
Create `/etc/nginx/conf.d/path-terminal-api.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or EC2 IP

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
```

**Ubuntu/Debian:**
Create `/etc/nginx/sites-available/path-terminal-api` (same content as above), then:

```bash
sudo ln -s /etc/nginx/sites-available/path-terminal-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
```

Test and restart:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable path-terminal-api
sudo systemctl start path-terminal-api
sudo systemctl status path-terminal-api
```

### 8. Configure Firewall

**Amazon Linux 2023:**
```bash
# Enable and start firewalld
sudo systemctl enable firewalld
sudo systemctl start firewalld

# Add services
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

**Note:** Amazon Linux primarily uses AWS Security Groups for firewall rules. Ensure your Security Group allows:
- Port 22 (SSH)
- Port 80 (HTTP)
- Port 443 (HTTPS)

**Ubuntu:**
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## SSL/HTTPS Setup (Optional but Recommended)

For detailed SSL/HTTPS setup instructions, see [DOMAIN_SETUP.md](DOMAIN_SETUP.md)

### Quick Setup Using Script

**Amazon Linux 2023:**
```bash
cd /opt/path-terminal-api
sudo ./scripts/setup-ssl.sh posapi.path2ai.tech your-email@example.com
```

**Ubuntu:**
```bash
cd /opt/path-terminal-api
sudo ./scripts/setup-ssl.sh posapi.path2ai.tech your-email@example.com
```

### Manual Setup

**Amazon Linux 2023:**
```bash
# Install Certbot
sudo dnf update -y
sudo dnf install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d posapi.path2ai.tech

# Test renewal
sudo certbot renew --dry-run
```

**Ubuntu:**
```bash
# Install Certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d posapi.path2ai.tech

# Test renewal
sudo certbot renew --dry-run
```

The certificate will auto-renew. For complete setup instructions including DNS configuration, see [DOMAIN_SETUP.md](DOMAIN_SETUP.md).

## Updating the Application

### Method 1: Git Pull (Recommended)

```bash
cd /opt/path-terminal-api
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart path-terminal-api
```

### Method 2: Using Update Script

```bash
cd /opt/path-terminal-api
./scripts/update.sh
```

## Monitoring

### Check Service Status

```bash
sudo systemctl status path-terminal-api
```

### View Logs

```bash
sudo journalctl -u path-terminal-api -f
```

### Check Nginx Status

```bash
sudo systemctl status nginx
sudo nginx -t
```

## Troubleshooting

### Service Won't Start - "Failed to locate executable uvicorn"

This error means the virtual environment wasn't created properly or dependencies weren't installed.

**Quick Fix:**
```bash
# Run the verification script
cd /opt/path-terminal-api
sudo ./scripts/verify-install.sh

# Then restart the service
sudo systemctl daemon-reload
sudo systemctl restart path-terminal-api
```

**Manual Fix:**
```bash
cd /opt/path-terminal-api/backend

# Remove broken venv if it exists
sudo rm -rf venv

# Recreate virtual environment
python3.11 -m venv venv || python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify uvicorn exists
ls -la venv/bin/uvicorn

# Fix permissions
sudo chown -R ec2-user:ec2-user /opt/path-terminal-api

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart path-terminal-api
```

### Service Won't Start - Other Issues

1. Check logs: `sudo journalctl -u path-terminal-api -n 50`
2. Verify Python path: `which python3`
3. Check virtual environment: `ls -la /opt/path-terminal-api/backend/venv`
4. Verify uvicorn exists: `ls -la /opt/path-terminal-api/backend/venv/bin/uvicorn`
5. Verify port availability: `sudo netstat -tulpn | grep 8000`
6. Check file permissions: `ls -la /opt/path-terminal-api/backend/venv/bin/`

### Nginx Issues

1. Test configuration: `sudo nginx -t`
2. Check error logs: `sudo tail -f /var/log/nginx/error.log`
3. Verify proxy settings match service port

### Permission Issues

```bash
sudo chown -R ubuntu:ubuntu /opt/path-terminal-api
```

## Backup

Before major updates, backup the application:

```bash
sudo cp -r /opt/path-terminal-api /opt/path-terminal-api-backup-$(date +%Y%m%d)
```

## Rollback

If an update causes issues:

```bash
sudo systemctl stop path-terminal-api
sudo rm -rf /opt/path-terminal-api
sudo cp -r /opt/path-terminal-api-backup-YYYYMMDD /opt/path-terminal-api
sudo systemctl start path-terminal-api
```

## Environment Variables

Edit the systemd service file to modify environment variables:

```bash
sudo nano /etc/systemd/system/path-terminal-api.service
sudo systemctl daemon-reload
sudo systemctl restart path-terminal-api
```

## Security Considerations

1. **Firewall**: Only open necessary ports (22, 80, 443)
2. **SSH Keys**: Use SSH keys instead of passwords
3. **HTTPS**: Always use HTTPS in production
4. **Environment Variables**: Don't commit sensitive data
5. **Regular Updates**: Keep system packages updated

```bash
sudo apt update && sudo apt upgrade -y
```

## Performance Tuning

For production, consider:

1. **Gunicorn with Uvicorn Workers**:
   ```bash
   pip install gunicorn
   ```
   Update systemd service:
   ```ini
   ExecStart=/opt/path-terminal-api/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. **Increase Worker Processes**: Adjust `-w` parameter based on CPU cores

3. **Nginx Caching**: Add caching for static assets

## Support

For issues or questions, refer to the main [README.md](README.md) or visit [path2ai.tech](https://path2ai.tech)

