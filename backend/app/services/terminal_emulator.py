"""
Terminal emulator service - core logic for emulating payment terminal behavior
"""
import time
import os
from typing import Dict, Any, Optional
from datetime import datetime
from .session_manager import SessionManager, Session


class TerminalEmulator:
    """Emulates payment terminal behavior"""
    
    def __init__(self):
        self.session_manager = SessionManager(
            timeout_minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
        )
        self.ack_only = os.getenv("ACK_ONLY", "false").lower() == "true"
        self.response_delay_ms = int(os.getenv("RESPONSE_DELAY_MS", "500"))
        self.transaction_counter = int(time.time())
        
    def generate_txn_id(self, prefix: str = "T") -> str:
        """Generate a transaction ID"""
        self.transaction_counter += 1
        return f"{prefix}{self.transaction_counter}"
    
    def generate_auth_code(self) -> str:
        """Generate an authorization code"""
        return f"{int(time.time()) % 1000000:06d}"
    
    def process_login(self, req_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process login request"""
        user = args.get("user", "default")
        session_id = f"sess_{int(time.time())}"
        session = self.session_manager.create_session(session_id, user)
        
        return {
            "type": "result",
            "req_id": req_id,
            "cmd": "Login",
            "status": "success",
            "user": user,
            "session_id": session_id,
            "capabilities": {
                "emv": True,
                "contactless": True,
                "magstripe": True,
                "version": "1.0"
            },
            "ts": datetime.now().isoformat()
        }
    
    def process_logout(self, req_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process logout request"""
        if session_id:
            self.session_manager.end_session(session_id)
        
        return {
            "type": "result",
            "req_id": req_id,
            "cmd": "Logout",
            "status": "success",
            "ts": datetime.now().isoformat()
        }
    
    def process_sale(self, req_id: str, args: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process sale request"""
        amount = args.get("amount", 0)
        txn_id = self.generate_txn_id("T")
        auth_code = self.generate_auth_code()
        
        # Add to session if available
        if session_id:
            session = self.session_manager.get_session(session_id)
            if session:
                session.add_transaction(txn_id, "Sale", amount)
        
        return {
            "type": "result",
            "req_id": req_id,
            "cmd": "Sale",
            "status": "success",
            "txn_id": txn_id,
            "auth_code": auth_code,
            "amount": amount,
            "ts": datetime.now().isoformat()
        }
    
    def process_refund(self, req_id: str, args: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process refund request"""
        amount = args.get("amount", 0)
        original_txn_id = args.get("original_txn_id")
        txn_id = self.generate_txn_id("R")
        
        if session_id:
            session = self.session_manager.get_session(session_id)
            if session:
                session.add_transaction(txn_id, "Refund", amount)
        
        return {
            "type": "result",
            "req_id": req_id,
            "cmd": "Refund",
            "status": "success",
            "txn_id": txn_id,
            "original_txn_id": original_txn_id,
            "amount": amount,
            "ts": datetime.now().isoformat()
        }
    
    def process_reversal(self, req_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process reversal request"""
        txn_id = args.get("txn_id")
        
        return {
            "type": "result",
            "req_id": req_id,
            "cmd": "Reversal",
            "status": "success",
            "txn_id": txn_id,
            "ts": datetime.now().isoformat()
        }
    
    def process_cancellation(self, req_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process cancellation request"""
        txn_id = args.get("txn_id")
        
        return {
            "type": "result",
            "req_id": req_id,
            "cmd": "Cancellation",
            "status": "success",
            "txn_id": txn_id,
            "ts": datetime.now().isoformat()
        }
    
    def process_completion(self, req_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process completion advice request"""
        txn_id = args.get("txn_id")
        
        return {
            "type": "result",
            "req_id": req_id,
            "cmd": "Completion",
            "status": "success",
            "txn_id": txn_id,
            "ts": datetime.now().isoformat()
        }
    
    def process_auto_reversal(self, req_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process auto-reversal request"""
        txn_id = args.get("txn_id")
        reason = args.get("reason", "network_error")
        
        return {
            "type": "result",
            "req_id": req_id,
            "cmd": "AutoReversal",
            "status": "success",
            "txn_id": txn_id,
            "reason": reason,
            "ts": datetime.now().isoformat()
        }
    
    def process_loyalty(self, req_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process loyalty request"""
        card_number = args.get("card_number")
        action = args.get("action", "enquiry")
        
        return {
            "type": "result",
            "req_id": req_id,
            "cmd": "Loyalty",
            "status": "success",
            "action": action,
            "points": 1000 if action == "enquiry" else None,
            "ts": datetime.now().isoformat()
        }
    
    def create_ack(self, req_id: str, cmd: str, accepted: bool = True) -> Dict[str, Any]:
        """Create ACK response"""
        return {
            "type": "ack",
            "req_id": req_id,
            "cmd": cmd,
            "status": "accepted" if accepted else "rejected"
        }
    
    def should_send_result(self) -> bool:
        """Check if result should be sent (not ACK_ONLY mode)"""
        return not self.ack_only

