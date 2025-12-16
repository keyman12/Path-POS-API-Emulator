"""
Response models matching the demo JSON format
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ACKResponse(BaseModel):
    """ACK response - always sent first"""
    type: str = Field(default="ack", description="Response type")
    req_id: str = Field(..., description="Request ID from original request")
    cmd: str = Field(..., description="Command name")
    status: str = Field(..., description="Status: accepted or rejected")


class ResultResponse(BaseModel):
    """Result response - sent after ACK (if not ACK_ONLY mode)"""
    type: str = Field(default="result", description="Response type")
    req_id: str = Field(..., description="Request ID from original request")
    cmd: str = Field(..., description="Command name")
    status: str = Field(..., description="Status: success or fail")
    txn_id: Optional[str] = Field(None, description="Transaction ID")
    auth_code: Optional[str] = Field(None, description="Authorization code")
    user: Optional[str] = Field(None, description="User identifier (for Login)")
    ts: Optional[str] = Field(None, description="Timestamp")
    reason: Optional[str] = Field(None, description="Error reason (if status is fail)")
    detail: Optional[str] = Field(None, description="Error detail (if status is fail)")


class TerminalCapabilities(BaseModel):
    """Terminal capabilities returned on Login"""
    emv: bool = Field(default=True, description="EMV chip support")
    contactless: bool = Field(default=True, description="Contactless support")
    magstripe: bool = Field(default=True, description="Magnetic stripe support")
    version: str = Field(default="1.0", description="Terminal version")


class LoginResponse(ResultResponse):
    """Login response with terminal capabilities"""
    capabilities: Optional[TerminalCapabilities] = Field(None, description="Terminal capabilities")

