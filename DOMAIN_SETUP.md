# Domain and HTTPS Setup Guide

## Overview

This guide covers setting up `posapi.path2ai.tech` with HTTPS using Let's Encrypt.

## Prerequisites

1. **Domain DNS Access**: You need access to DNS settings for `path2ai.tech`
2. **EC2 Instance**: Running Ubuntu with the application deployed
3. **Elastic IP**: Static IP address from AWS (recommended)

## Step 1: Configure AWS Elastic IP

1. **Allocate Elastic IP**:
   - Go to AWS Console → EC2 → Elastic IPs
   - Click "Allocate Elastic IP address"
   - Select your region
   - Click "Allocate"

2. **Associate with EC2 Instance**:
   - Select the Elastic IP
   - Click "Actions" → "Associate Elastic IP address"
   - Choose your EC2 instance
   - Click "Associate"

3. **Note the IP Address**: You'll need this for DNS configuration

## Step 2: Configure DNS

1. **Go to your DNS provider** (where path2ai.tech is managed)

2. **Add A Record**:
   - **Type**: A
   - **Name**: `posapi` (or `posapi.path2ai.tech` depending on provider)
   - **Value**: Your Elastic IP address
   - **TTL**: 300 (or default)

3. **Verify DNS Propagation**:
   ```bash
   # Check if DNS is resolving
   dig posapi.path2ai.tech
   # or
   nslookup posapi.path2ai.tech
   ```

   Wait 5-15 minutes for DNS to propagate.

## Step 3: Update Nginx Configuration

Update the Nginx configuration to use your domain:

```bash
sudo nano /etc/nginx/sites-available/path-terminal-api
```

Change the `server_name` line:

```nginx
server {
    listen 80;
    server_name posapi.path2ai.tech;  # Update this line
    
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

Test and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Step 4: Install Certbot (Let's Encrypt)

```bash
# Update system
sudo apt update

# Install Certbot and Nginx plugin
sudo apt install certbot python3-certbot-nginx
```

## Step 5: Obtain SSL Certificate

```bash
# Request certificate (Certbot will automatically configure Nginx)
sudo certbot --nginx -d posapi.path2ai.tech

# Follow the prompts:
# - Enter your email address
# - Agree to terms of service
# - Choose whether to redirect HTTP to HTTPS (recommended: Yes)
```

Certbot will:
- Automatically obtain the certificate
- Update Nginx configuration for HTTPS
- Set up automatic renewal

## Step 6: Verify HTTPS

1. **Test in browser**: https://posapi.path2ai.tech
2. **Check certificate**: Should show valid Let's Encrypt certificate
3. **Test API**: https://posapi.path2ai.tech/docs

## Step 7: Automatic Certificate Renewal

Certbot sets up automatic renewal, but verify it's working:

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer
```

Certificates auto-renew 30 days before expiration.

## Step 8: Update CORS Configuration (Production)

For production, update CORS to only allow your domain:

```bash
# Edit the main.py file
sudo nano /opt/path-terminal-api/backend/app/main.py
```

Update CORS middleware:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://posapi.path2ai.tech", "https://path2ai.tech"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Restart the service:
```bash
sudo systemctl restart path-terminal-api
```

**Note**: The current configuration allows all origins (`allow_origins=["*"]`) which is fine for development but should be restricted in production.

## Troubleshooting

### DNS Not Resolving

```bash
# Check DNS propagation
dig posapi.path2ai.tech
nslookup posapi.path2ai.tech

# Wait 15-30 minutes for full propagation
```

### Certificate Request Fails

1. **Check DNS is resolving**:
   ```bash
   dig posapi.path2ai.tech
   ```

2. **Check port 80 is open**:
   ```bash
   sudo ufw status
   sudo ufw allow 80/tcp
   ```

3. **Check Nginx is running**:
   ```bash
   sudo systemctl status nginx
   ```

4. **Check firewall on EC2 Security Group**:
   - Ensure port 80 and 443 are open in AWS Security Group

### Mixed Content Warnings

If you see mixed content warnings, ensure:
- All API calls use HTTPS
- WebSocket connections use `wss://` instead of `ws://`

Update frontend if needed:
```javascript
// In app.js, update WebSocket URL
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/ws`;
```

## Security Headers (Optional but Recommended)

Add security headers to Nginx:

```nginx
server {
    # ... existing config ...
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

## Verification Checklist

- [ ] DNS A record points to Elastic IP
- [ ] DNS resolves correctly (`dig posapi.path2ai.tech`)
- [ ] HTTP works (http://posapi.path2ai.tech)
- [ ] SSL certificate obtained
- [ ] HTTPS works (https://posapi.path2ai.tech)
- [ ] Certificate auto-renewal configured
- [ ] API docs accessible via HTTPS
- [ ] WebSocket works via WSS

## Next Steps

1. **Monitor logs**: `sudo journalctl -u path-terminal-api -f`
2. **Set up monitoring**: Consider CloudWatch or similar
3. **Backup certificates**: Certificates are stored in `/etc/letsencrypt/`

