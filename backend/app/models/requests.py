"""
Request models matching the demo JSON format
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class BaseRequest(BaseModel):
    """Base request model matching demo format"""
    cmd: str = Field(..., description="Command name (Sale, Refund, Login, etc.)")
    req_id: str = Field(..., description="Unique request identifier")
    args: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Command arguments")


class LoginRequest(BaseRequest):
    """Login request - establish session"""
    cmd: str = Field(default="Login", description="Login command")
    args: Dict[str, Any] = Field(default_factory=lambda: {"user": "default"}, description="Login arguments")


class LogoutRequest(BaseRequest):
    """Logout request - end session"""
    cmd: str = Field(default="Logout", description="Logout command")


class SaleRequest(BaseRequest):
    """Sale/Payment request"""
    cmd: str = Field(default="Sale", description="Sale command")
    args: Dict[str, Any] = Field(..., description="Sale arguments including amount")


class RefundRequest(BaseRequest):
    """Refund request"""
    cmd: str = Field(default="Refund", description="Refund command")
    args: Dict[str, Any] = Field(..., description="Refund arguments including amount and original txn_id")


class ReversalRequest(BaseRequest):
    """Reversal request"""
    cmd: str = Field(default="Reversal", description="Reversal command")
    args: Dict[str, Any] = Field(..., description="Reversal arguments including txn_id")


class CancellationRequest(BaseRequest):
    """Cancellation request"""
    cmd: str = Field(default="Cancellation", description="Cancellation command")
    args: Dict[str, Any] = Field(..., description="Cancellation arguments including txn_id")


class CompletionRequest(BaseRequest):
    """Completion advice request"""
    cmd: str = Field(default="Completion", description="Completion command")
    args: Dict[str, Any] = Field(..., description="Completion arguments")


class AutoReversalRequest(BaseRequest):
    """Auto-reversal request for error recovery"""
    cmd: str = Field(default="AutoReversal", description="Auto-reversal command")
    args: Dict[str, Any] = Field(..., description="Auto-reversal arguments")


class LoyaltyRequest(BaseRequest):
    """Loyalty management request"""
    cmd: str = Field(default="Loyalty", description="Loyalty command")
    args: Dict[str, Any] = Field(..., description="Loyalty arguments")

