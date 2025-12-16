"""
WebSocket endpoint for real-time bidirectional communication
"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any
from ..services.terminal_emulator import TerminalEmulator

router = APIRouter()
emulator = TerminalEmulator()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time terminal emulation"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                obj = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "reason": "invalid_json",
                    "detail": "Failed to parse JSON"
                })
                continue
            
            cmd = str(obj.get("cmd", "")).strip()
            req_id = str(obj.get("req_id", "")).strip()
            args = obj.get("args", {})
            
            # Known commands
            known = cmd in ("Sale", "Refund", "Reversal", "Login", "Logout", 
                          "Cancellation", "Completion", "AutoReversal", "Loyalty")
            
            # Send ACK
            ack = emulator.create_ack(req_id, cmd, accepted=known)
            await websocket.send_json(ack)
            
            # Process command if known and not ACK_ONLY
            if known and emulator.should_send_result():
                try:
                    if cmd == "Login":
                        result = emulator.process_login(req_id, args)
                    elif cmd == "Logout":
                        session_id = args.get("session_id")
                        result = emulator.process_logout(req_id, session_id)
                    elif cmd == "Sale":
                        session_id = args.get("session_id")
                        result = emulator.process_sale(req_id, args, session_id)
                    elif cmd == "Refund":
                        session_id = args.get("session_id")
                        result = emulator.process_refund(req_id, args, session_id)
                    elif cmd == "Reversal":
                        result = emulator.process_reversal(req_id, args)
                    elif cmd == "Cancellation":
                        result = emulator.process_cancellation(req_id, args)
                    elif cmd == "Completion":
                        result = emulator.process_completion(req_id, args)
                    elif cmd == "AutoReversal":
                        result = emulator.process_auto_reversal(req_id, args)
                    elif cmd == "Loyalty":
                        result = emulator.process_loyalty(req_id, args)
                    else:
                        result = None
                    
                    if result:
                        await websocket.send_json(result)
                except Exception as e:
                    await websocket.send_json({
                        "type": "result",
                        "req_id": req_id,
                        "cmd": cmd,
                        "status": "fail",
                        "reason": "exception",
                        "detail": str(e)
                    })
                    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "reason": "server_error",
                "detail": str(e)
            })
        except:
            pass

