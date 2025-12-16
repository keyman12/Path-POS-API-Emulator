"""
Loyalty Management endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..models.requests import BaseRequest
from ..services.terminal_emulator import TerminalEmulator

router = APIRouter(prefix="/api/v1/loyalty", tags=["Loyalty"])
emulator = TerminalEmulator()


@router.post("", response_model=Dict[str, Any])
async def loyalty(request: BaseRequest):
    """LoyaltyRequest - Manage loyalty cards, points, discounts"""
    try:
        if request.cmd != "Loyalty":
            raise HTTPException(status_code=400, detail="Command must be 'Loyalty'")
        
        ack = emulator.create_ack(request.req_id, request.cmd, accepted=True)
        result = emulator.process_loyalty(request.req_id, request.args or {})
        
        return {
            "ack": ack,
            "result": result if emulator.should_send_result() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/response", response_model=Dict[str, Any])
async def loyalty_response(request: BaseRequest):
    """LoyaltyResponse - Handle loyalty response"""
    try:
        ack = emulator.create_ack(request.req_id, request.cmd, accepted=True)
        
        return {
            "ack": ack,
            "result": None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

