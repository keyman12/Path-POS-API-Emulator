"""
Auto-Reversal endpoints for error recovery
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..models.requests import BaseRequest
from ..services.terminal_emulator import TerminalEmulator

router = APIRouter(prefix="/api/v1", tags=["Auto-Reversal"])
emulator = TerminalEmulator()


@router.post("/auto-reversal", response_model=Dict[str, Any])
async def auto_reversal(request: BaseRequest):
    """AutoReversal/NegativeCompletionAdvice - Reverse orphan transactions after errors"""
    try:
        if request.cmd != "AutoReversal":
            raise HTTPException(status_code=400, detail="Command must be 'AutoReversal'")
        
        ack = emulator.create_ack(request.req_id, request.cmd, accepted=True)
        result = emulator.process_auto_reversal(request.req_id, request.args or {})
        
        return {
            "ack": ack,
            "result": result if emulator.should_send_result() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

