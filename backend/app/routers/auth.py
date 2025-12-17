"""
Authentication endpoints - Login/Logout
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..models.requests import BaseRequest, LoginRequest, LogoutRequest
from ..models.responses import ACKResponse, ResultResponse
from ..services.terminal_emulator import get_emulator

router = APIRouter(prefix="/api/v1", tags=["Authentication"])
emulator = get_emulator()  # Use shared singleton instance


@router.post("/login", response_model=Dict[str, Any])
async def login(request: BaseRequest):
    """Login - Establish session and return terminal capabilities"""
    try:
        # Create ACK
        ack = emulator.create_ack(request.req_id, request.cmd, accepted=True)
        
        # Process login
        result = emulator.process_login(request.req_id, request.args or {})
        
        return {
            "ack": ack,
            "result": result if emulator.should_send_result() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout", response_model=Dict[str, Any])
async def logout(request: BaseRequest):
    """Logout - End session"""
    try:
        session_id = (request.args or {}).get("session_id")
        ack = emulator.create_ack(request.req_id, request.cmd, accepted=True)
        result = emulator.process_logout(request.req_id, session_id)
        
        return {
            "ack": ack,
            "result": result if emulator.should_send_result() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

