# AWS EC2 Deployment Guide

## Prerequisites on EC2 Instance

Before deploying, ensure your EC2 instance has:

### 1. Operating System
- **Ubuntu 22.04 LTS** (recommended) or Ubuntu 20.04 LTS
- Or Amazon Linux 2023

### 2. Required Software

#### Python 3.10 or 3.11
```bash
# Check Python version
python3 --version

# Ubuntu - Python should be pre-installed
# If not, install:
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### Git
```bash
# Install Git
sudo apt update
sudo apt install git

# Verify
git --version
```

#### Nginx (Web Server)
```bash
# Install Nginx
sudo apt update
sudo apt install nginx

# Verify
nginx -v
```

#### Systemd (Service Manager)
- Pre-installed on Ubuntu/Amazon Linux
- Used to run the application as a service

### 3. Network Configuration

#### Security Group Rules
Ensure your EC2 security group allows:
- **Port 22** (SSH) - from your IP
- **Port 80** (HTTP) - from anywhere (0.0.0.0/0)
- **Port 443** (HTTPS) - from anywhere (0.0.0.0/0) - if using SSL

#### Firewall (UFW)
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Quick Deployment Steps

### Option 1: Automated Deployment Script

1. **Connect to EC2**:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

2. **Clone and run deploy script**:
   ```bash
   cd /opt
   sudo git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git path-terminal-api
   cd path-terminal-api
   sudo chmod +x scripts/deploy.sh
   sudo ./scripts/deploy.sh https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   ```

### Option 2: Manual Deployment

Follow the detailed steps in [DEPLOY.md](DEPLOY.md)

## What Gets Installed

The deployment script automatically installs:
- ✅ Python 3.10/3.11 and pip
- ✅ Python virtual environment
- ✅ All Python dependencies (from requirements.txt)
- ✅ Nginx web server
- ✅ Systemd service configuration
- ✅ Firewall rules

## Service Management

After deployment, manage the service with:

```bash
# Check status
sudo systemctl status path-terminal-api

# Start service
sudo systemctl start path-terminal-api

# Stop service
sudo systemctl stop path-terminal-api

# Restart service
sudo systemctl restart path-terminal-api

# View logs
sudo journalctl -u path-terminal-api -f
```

## Updating from GitHub

After pushing changes to GitHub:

```bash
cd /opt/path-terminal-api
sudo ./scripts/update.sh
```

Or manually:
```bash
cd /opt/path-terminal-api
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart path-terminal-api
```

## Verification Checklist

After deployment, verify:

- [ ] Service is running: `sudo systemctl status path-terminal-api`
- [ ] Nginx is running: `sudo systemctl status nginx`
- [ ] Can access web interface: `http://your-ec2-ip`
- [ ] API docs accessible: `http://your-ec2-ip/docs`
- [ ] Health endpoint works: `curl http://your-ec2-ip/health`
- [ ] Logs show no errors: `sudo journalctl -u path-terminal-api -n 50`

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.

## Domain and HTTPS Setup

For setting up `posapi.path2ai.tech` with HTTPS, see [DOMAIN_SETUP.md](DOMAIN_SETUP.md)

Quick setup:
```bash
# After deployment, set up SSL
sudo ./scripts/setup-ssl.sh posapi.path2ai.tech
```

**Prerequisites for HTTPS**:
1. DNS A record pointing to EC2 Elastic IP
2. Port 80 and 443 open in Security Group
3. Domain DNS propagated (check with `dig posapi.path2ai.tech`)

## Next Steps

1. **Set up domain and HTTPS**: See [DOMAIN_SETUP.md](DOMAIN_SETUP.md)
2. **Configure Elastic IP**: Allocate and associate with EC2 instance
3. **Update DNS**: Point `posapi.path2ai.tech` to Elastic IP

3. **Monitor logs**:
   ```bash
   sudo journalctl -u path-terminal-api -f
   ```

