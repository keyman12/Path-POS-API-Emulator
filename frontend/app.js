// Path Payment Terminal API Emulator - Frontend JavaScript

const API_BASE = window.location.origin;

// API Tester
const cmdSelect = document.getElementById('cmd-select');
const reqIdInput = document.getElementById('req-id');
const argsInput = document.getElementById('args-input');
const endpointSelect = document.getElementById('endpoint-select');
const sendBtn = document.getElementById('send-btn');
const responseDisplay = document.getElementById('response-display');

// Update endpoint when command changes
cmdSelect.addEventListener('change', () => {
    const cmd = cmdSelect.value;
    const endpointMap = {
        'Login': '/api/v1/login',
        'Logout': '/api/v1/logout',
        'Sale': '/api/v1/payment/sale',
        'Refund': '/api/v1/payment/refund',
        'Reversal': '/api/v1/reversal',
        'Cancellation': '/api/v1/cancellation',
        'Completion': '/api/v1/completion',
        'AutoReversal': '/api/v1/auto-reversal',
        'Loyalty': '/api/v1/loyalty'
    };
    endpointSelect.value = endpointMap[cmd] || '/api/v1/login';
    
    // Update default args
    if (cmd === 'Sale' || cmd === 'Refund') {
        argsInput.value = JSON.stringify({ amount: 10000, session_id: '' }, null, 2);
    } else if (cmd === 'Login') {
        argsInput.value = JSON.stringify({ user: 'default' }, null, 2);
    } else {
        argsInput.value = JSON.stringify({}, null, 2);
    }
});

sendBtn.addEventListener('click', async () => {
    try {
        const cmd = cmdSelect.value;
        const reqId = reqIdInput.value || `req_${Date.now()}`;
        let args = {};
        
        try {
            args = JSON.parse(argsInput.value);
        } catch (e) {
            responseDisplay.textContent = `Error: Invalid JSON in arguments\n${e.message}`;
            return;
        }
        
        const request = {
            cmd: cmd,
            req_id: reqId,
            args: args
        };
        
        const endpoint = endpointSelect.value;
        
        responseDisplay.textContent = 'Sending request...\n\n' + JSON.stringify(request, null, 2);
        
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request)
        });
        
        const data = await response.json();
        
        responseDisplay.textContent = `Status: ${response.status} ${response.statusText}\n\n` + 
                                     JSON.stringify(data, null, 2);
        
    } catch (error) {
        responseDisplay.textContent = `Error: ${error.message}`;
    }
});

// WebSocket Tester
const wsConnectBtn = document.getElementById('ws-connect-btn');
const wsDisconnectBtn = document.getElementById('ws-disconnect-btn');
const wsStatus = document.getElementById('ws-status');
const wsMessageLog = document.getElementById('ws-message-log');
const wsMessageInput = document.getElementById('ws-message-input');
const wsSendBtn = document.getElementById('ws-send-btn');

let ws = null;

function updateWSStatus(connected) {
    if (connected) {
        wsStatus.textContent = 'Connected';
        wsStatus.style.backgroundColor = '#2A9D8F';
        wsStatus.style.color = '#FFFFFF';
        wsConnectBtn.disabled = true;
        wsDisconnectBtn.disabled = false;
        wsSendBtn.disabled = false;
    } else {
        wsStatus.textContent = 'Disconnected';
        wsStatus.style.backgroundColor = '#E63946';
        wsStatus.style.color = '#FFFFFF';
        wsConnectBtn.disabled = false;
        wsDisconnectBtn.disabled = true;
        wsSendBtn.disabled = true;
    }
}

function addWSMessage(message, type) {
    const div = document.createElement('div');
    div.className = `message ${type}`;
    div.textContent = `${new Date().toLocaleTimeString()} [${type.toUpperCase()}]: ${JSON.stringify(message, null, 2)}`;
    wsMessageLog.appendChild(div);
    wsMessageLog.scrollTop = wsMessageLog.scrollHeight;
}

wsConnectBtn.addEventListener('click', () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        updateWSStatus(true);
        addWSMessage({ type: 'connection', status: 'opened' }, 'sent');
    };
    
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            addWSMessage(data, 'received');
        } catch (e) {
            addWSMessage({ error: 'Invalid JSON', raw: event.data }, 'received');
        }
    };
    
    ws.onerror = (error) => {
        addWSMessage({ type: 'error', error: error }, 'received');
    };
    
    ws.onclose = () => {
        updateWSStatus(false);
        addWSMessage({ type: 'connection', status: 'closed' }, 'sent');
    };
});

wsDisconnectBtn.addEventListener('click', () => {
    if (ws) {
        ws.close();
        ws = null;
    }
});

wsSendBtn.addEventListener('click', () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('WebSocket not connected');
        return;
    }
    
    try {
        const message = JSON.parse(wsMessageInput.value);
        ws.send(JSON.stringify(message));
        addWSMessage(message, 'sent');
        wsMessageInput.value = '';
    } catch (e) {
        alert(`Invalid JSON: ${e.message}`);
    }
});

// Initialize
updateWSStatus(false);

