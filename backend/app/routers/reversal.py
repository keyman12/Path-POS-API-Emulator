"""
Reversal & Cancellation endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..models.requests import BaseRequest
from ..services.terminal_emulator import TerminalEmulator

router = APIRouter(prefix="/api/v1", tags=["Reversal"])
emulator = TerminalEmulator()


@router.post("/reversal", response_model=Dict[str, Any])
async def reversal(request: BaseRequest):
    """ReversalRequest - Reverse a transaction"""
    try:
        if request.cmd != "Reversal":
            raise HTTPException(status_code=400, detail="Command must be 'Reversal'")
        
        ack = emulator.create_ack(request.req_id, request.cmd, accepted=True)
        result = emulator.process_reversal(request.req_id, request.args or {})
        
        return {
            "ack": ack,
            "result": result if emulator.should_send_result() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancellation", response_model=Dict[str, Any])
async def cancellation(request: BaseRequest):
    """CancellationRequest - Cancel a transaction"""
    try:
        if request.cmd != "Cancellation":
            raise HTTPException(status_code=400, detail="Command must be 'Cancellation'")
        
        ack = emulator.create_ack(request.req_id, request.cmd, accepted=True)
        result = emulator.process_cancellation(request.req_id, request.args or {})
        
        return {
            "ack": ack,
            "result": result if emulator.should_send_result() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

