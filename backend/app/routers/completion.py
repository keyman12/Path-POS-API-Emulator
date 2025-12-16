"""
Completion Advice endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..models.requests import BaseRequest
from ..services.terminal_emulator import TerminalEmulator

router = APIRouter(prefix="/api/v1/completion", tags=["Completion"])
emulator = TerminalEmulator()


@router.post("", response_model=Dict[str, Any])
async def completion(request: BaseRequest):
    """CompletionRequest - Finalize and capture a previously authorized transaction"""
    try:
        if request.cmd != "Completion":
            raise HTTPException(status_code=400, detail="Command must be 'Completion'")
        
        ack = emulator.create_ack(request.req_id, request.cmd, accepted=True)
        result = emulator.process_completion(request.req_id, request.args or {})
        
        return {
            "ack": ack,
            "result": result if emulator.should_send_result() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/response", response_model=Dict[str, Any])
async def completion_response(request: BaseRequest):
    """CompletionResponse - Handle completion response"""
    try:
        ack = emulator.create_ack(request.req_id, request.cmd, accepted=True)
        
        return {
            "ack": ack,
            "result": None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

