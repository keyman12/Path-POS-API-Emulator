# Path Payment Terminal API Emulator

API emulator for testing iOS/Android payment terminal integrations. This service emulates payment terminal endpoints, allowing developers to test their payment flows without physical hardware.

## Features

- **REST API** - Standard HTTP endpoints for all payment operations
- **WebSocket Support** - Real-time bidirectional communication (mimics BLE behavior)
- **7 API Categories**:
  - Authentication (Login/Logout)
  - Payment Initiation (Sale, Refund)
  - Reversal & Cancellation
  - Completion Advice
  - Auto-Reversal
  - Loyalty Management
- **Branded Web Interface** - Path-branded UI for testing and documentation
- **OpenAPI Documentation** - Auto-generated API docs for MCP integration

## Quick Start

### Local Development

**Note**: Python 3.10, 3.11, or 3.12 is recommended. Python 3.13 may have compatibility issues with some dependencies.

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd APIs
   ```

2. **Create virtual environment**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   
   **If using Python 3.13 and encountering build errors**, use Python 3.11 or 3.12:
   ```bash
   # macOS (using Homebrew)
   brew install python@3.11
   python3.11 -m venv venv
   
   # Or use pyenv
   pyenv install 3.11.9
   pyenv local 3.11.9
   python -m venv venv
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional)
   ```bash
   export ACK_ONLY=false
   export RESPONSE_DELAY_MS=500
   export SESSION_TIMEOUT_MINUTES=30
   export PORT=8000
   ```

5. **Run the server**
   ```bash
   # Option 1: Using the run script (recommended)
   ./run.sh
   
   # Option 2: Direct uvicorn command
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude "venv/*"
   
   # Option 3: Without reload (if reload causes issues)
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

6. **Access the web interface**
   - Open http://localhost:8000 in your browser
   - API docs: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /api/v1/login` - Establish session, return terminal capabilities
- `POST /api/v1/logout` - End session

### Payment
- `POST /api/v1/payment/sale` - PaymentRequest (SaleRequest)
- `POST /api/v1/payment/refund` - RefundRequest
- `POST /api/v1/payment/response` - PaymentResponse

### Reversal & Cancellation
- `POST /api/v1/reversal` - ReversalRequest
- `POST /api/v1/cancellation` - CancellationRequest

### Completion Advice
- `POST /api/v1/completion` - CompletionRequest
- `POST /api/v1/completion/response` - CompletionResponse

### Auto-Reversal
- `POST /api/v1/auto-reversal` - AutoReversal/NegativeCompletionAdvice

### Loyalty Management
- `POST /api/v1/loyalty` - LoyaltyRequest
- `POST /api/v1/loyalty/response` - LoyaltyResponse

### WebSocket
- `WS /ws` - Real-time bidirectional communication

## Message Format

All APIs use JSON format matching the demo terminal code:

**Request:**
```json
{
  "cmd": "Sale",
  "req_id": "req_123",
  "args": {
    "amount": 10000,
    "session_id": "sess_123"
  }
}
```

**Response (ACK first, then Result):**
```json
{
  "ack": {
    "type": "ack",
    "req_id": "req_123",
    "cmd": "Sale",
    "status": "accepted"
  },
  "result": {
    "type": "result",
    "req_id": "req_123",
    "cmd": "Sale",
    "status": "success",
    "txn_id": "T1234567890",
    "auth_code": "123456",
    "ts": "2024-01-01T12:00:00Z"
  }
}
```

## Configuration

Environment variables:

- `ACK_ONLY` - Set to `true` to send only ACK responses (default: `false`)
- `RESPONSE_DELAY_MS` - Simulated terminal processing delay in milliseconds (default: `500`)
- `SESSION_TIMEOUT_MINUTES` - Session timeout in minutes (default: `30`)
- `PORT` - Server port (default: `8000`)

## EC2 Deployment

See [DEPLOY.md](DEPLOY.md) for detailed EC2 deployment instructions.

## Updating the Application

The application can be easily updated via Git:

```bash
# On EC2 instance
cd /opt/path-terminal-api
git pull origin main
sudo systemctl restart path-terminal-api
```

Or use the provided update script:
```bash
./scripts/update.sh
```

## Project Structure

```
APIs/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models/              # Pydantic models
│   │   ├── routers/             # API route handlers
│   │   ├── services/            # Business logic
│   │   └── static/              # Static assets
│   └── requirements.txt
├── frontend/
│   ├── index.html              # Web interface
│   ├── styles.css              # Path-branded styling
│   └── app.js                  # Frontend JavaScript
├── scripts/                     # Deployment scripts
└── README.md
```

## License

Copyright © 2024 Path. All rights reserved.

## Support

For support, visit [path2ai.tech](https://path2ai.tech)

