"""
Payment endpoints - Sale, Refund, PaymentResponse
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..models.requests import BaseRequest
from ..services.terminal_emulator import get_emulator

router = APIRouter(prefix="/api/v1/payment", tags=["Payment"])
emulator = get_emulator()  # Use shared singleton instance


@router.post("/sale", response_model=Dict[str, Any])
async def sale(request: BaseRequest):
    """PaymentRequest (SaleRequest) - Initiate sale transaction"""
    try:
        if request.cmd != "Sale":
            raise HTTPException(status_code=400, detail="Command must be 'Sale'")
        
        ack = emulator.create_ack(request.req_id, request.cmd, accepted=True)
        session_id = (request.args or {}).get("session_id")
        result = emulator.process_sale(request.req_id, request.args or {}, session_id)
        
        return {
            "ack": ack,
            "result": result if emulator.should_send_result() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refund", response_model=Dict[str, Any])
async def refund(request: BaseRequest):
    """RefundRequest - Process refund transaction"""
    try:
        if request.cmd != "Refund":
            raise HTTPException(status_code=400, detail="Command must be 'Refund'")
        
        ack = emulator.create_ack(request.req_id, request.cmd, accepted=True)
        session_id = (request.args or {}).get("session_id")
        result = emulator.process_refund(request.req_id, request.args or {}, session_id)
        
        return {
            "ack": ack,
            "result": result if emulator.should_send_result() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/response", response_model=Dict[str, Any])
async def payment_response(request: BaseRequest):
    """PaymentResponse (SaleResponse) - Handle payment response"""
    try:
        ack = emulator.create_ack(request.req_id, request.cmd, accepted=True)
        
        return {
            "ack": ack,
            "result": None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

