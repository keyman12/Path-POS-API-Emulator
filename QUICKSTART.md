# Quick Start Guide

## What's Been Built

✅ **Complete Payment Terminal API Emulator** with:
- All 7 API categories (Auth, Payment, Reversal, Completion, Auto-Reversal, Loyalty)
- REST API endpoints
- WebSocket support for real-time communication
- Path-branded web interface
- OpenAPI documentation
- EC2 deployment scripts
- GitHub-ready structure

## Next Steps

### 1. Test Locally

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://localhost:8000 in your browser.

### 2. Push to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Path Payment Terminal API Emulator"

# Add your GitHub remote
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```

### 3. Deploy to EC2

**Option A: Using the deployment script**
```bash
# On your EC2 instance
sudo ./scripts/deploy.sh <your-github-repo-url>
```

**Option B: Manual deployment**
Follow the detailed instructions in [DEPLOY.md](DEPLOY.md)

### 4. Update Application

After making changes and pushing to GitHub:
```bash
# On EC2 instance
cd /opt/path-terminal-api
sudo ./scripts/update.sh
```

## Project Structure

```
APIs/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py      # FastAPI app entry point
│   │   ├── models/      # Request/Response models
│   │   ├── routers/     # API endpoints
│   │   └── services/    # Business logic
│   └── requirements.txt
├── frontend/            # Web interface
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── scripts/             # Deployment scripts
│   ├── deploy.sh        # Initial EC2 setup
│   └── update.sh        # Update from Git
├── README.md            # Main documentation
├── DEPLOY.md            # EC2 deployment guide
└── .gitignore
```

## Key Features

- **API Testing**: Use the web interface at `/` to test all endpoints
- **WebSocket Testing**: Real-time bidirectional communication tester
- **API Docs**: Auto-generated at `/docs` (Swagger) and `/redoc`
- **OpenAPI Spec**: Available at `/openapi.json` for MCP integration

## Configuration

Set environment variables to customize behavior:

- `ACK_ONLY=true` - Send only ACK responses (no result)
- `RESPONSE_DELAY_MS=500` - Simulate terminal processing delay
- `SESSION_TIMEOUT_MINUTES=30` - Session timeout
- `PORT=8000` - Server port

## Support

- Documentation: See [README.md](README.md)
- Deployment: See [DEPLOY.md](DEPLOY.md)
- Website: [path2ai.tech](https://path2ai.tech)

