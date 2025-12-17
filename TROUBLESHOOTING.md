# Troubleshooting Guide

## Common Issues

### "Attribute main:app not found in module app" Error

**Problem**: Uvicorn can't find the app module

**Solution**: 
1. Ensure you're in the `backend` directory
2. Use the run script: `./run.sh`
3. Or use explicit path: `uvicorn app.main:app --reload --reload-exclude "venv/*"`
4. If reload mode causes issues, run without reload: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

The issue is often caused by uvicorn's reload feature watching files in `venv/`, which causes reload loops. Exclude the venv directory from watching.

### Python 3.13 Compatibility Issues

**Problem**: `pydantic-core` fails to build with Python 3.13

**Solution**: Use Python 3.11 or 3.12 instead

```bash
# Check your Python version
python3 --version

# If it's 3.13, install Python 3.11 or 3.12

# Option 1: Using Homebrew (macOS)
brew install python@3.11
python3.11 -m venv venv
source venv/bin/activate

# Option 2: Using pyenv (recommended)
pyenv install 3.11.9
pyenv local 3.11.9
python -m venv venv
source venv/bin/activate

# Option 3: Download from python.org
# Visit https://www.python.org/downloads/ and install Python 3.11
```

### Virtual Environment Issues

**Problem**: `venv` module not found

**Solution**: Install python3-venv package

```bash
# Ubuntu/Debian
sudo apt install python3-venv

# macOS (usually pre-installed)
# If missing, reinstall Python via Homebrew
brew install python@3.11
```

### Port Already in Use

**Problem**: `Address already in use` error

**Solution**: Use a different port or kill the process

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001
```

### Import Errors

**Problem**: `ModuleNotFoundError` when running the app

**Solution**: Ensure you're in the correct directory and virtual environment is activated

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Not Loading

**Problem**: Web interface shows "Frontend not found"

**Solution**: Ensure frontend files are in the correct location

```bash
# Check directory structure
ls -la frontend/
ls -la backend/app/static/

# Frontend should be at: APIs/frontend/
# Static mount should point to: backend/app/static/
```

### WebSocket Connection Fails

**Problem**: WebSocket connection fails in browser

**Solution**: 
1. Check if server is running
2. Verify CORS settings in `main.py`
3. For production, ensure Nginx is configured for WebSocket upgrade

### EC2 Deployment Issues

**Problem**: Service won't start - "Failed to locate executable uvicorn"

**Solution**: Virtual environment not created or dependencies not installed

```bash
# Quick fix - run verification script
cd /opt/path-terminal-api
sudo ./scripts/verify-install.sh

# Then restart
sudo systemctl daemon-reload
sudo systemctl restart path-terminal-api
```

**Problem**: Service won't start on EC2 (general)

**Solution**: Check logs and permissions

```bash
# Check service status
sudo systemctl status path-terminal-api

# View logs
sudo journalctl -u path-terminal-api -n 50

# Check if venv exists and uvicorn is installed
ls -la /opt/path-terminal-api/backend/venv/bin/uvicorn

# If missing, recreate venv
cd /opt/path-terminal-api/backend
sudo rm -rf venv
python3.11 -m venv venv || python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Fix permissions (Amazon Linux)
sudo chown -R ec2-user:ec2-user /opt/path-terminal-api

# Fix permissions (Ubuntu)
sudo chown -R ubuntu:ubuntu /opt/path-terminal-api

# Verify Python path in service file
which python3
```

### Nginx 502 Bad Gateway

**Problem**: Nginx returns 502 error

**Solution**: 
1. Verify FastAPI service is running
2. Check Nginx error logs
3. Verify proxy_pass URL matches service port

```bash
# Check if service is running
sudo systemctl status path-terminal-api

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Test Nginx configuration
sudo nginx -t
```

## Getting Help

If you continue to experience issues:

1. Check the logs: `sudo journalctl -u path-terminal-api -f`
2. Verify all dependencies are installed: `pip list`
3. Check Python version: `python --version`
4. Review the [README.md](README.md) and [DEPLOY.md](DEPLOY.md)

For support, visit [path2ai.tech](https://path2ai.tech)

