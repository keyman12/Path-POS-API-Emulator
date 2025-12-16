"""
Session management for terminal emulator
"""
import time
from typing import Dict, Optional
from datetime import datetime, timedelta


class Session:
    """Represents an active session"""
    def __init__(self, session_id: str, user: str = "default"):
        self.session_id = session_id
        self.user = user
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_active = True
        self.transactions: list = []

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

    def add_transaction(self, txn_id: str, cmd: str, amount: Optional[float] = None):
        """Add a transaction to session history"""
        self.transactions.append({
            "txn_id": txn_id,
            "cmd": cmd,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        })


class SessionManager:
    """Manages active sessions"""
    def __init__(self, timeout_minutes: int = 30):
        self.sessions: Dict[str, Session] = {}
        self.timeout_minutes = timeout_minutes

    def create_session(self, session_id: str, user: str = "default") -> Session:
        """Create a new session"""
        session = Session(session_id, user)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get an active session"""
        session = self.sessions.get(session_id)
        if session and session.is_active:
            # Check timeout
            if datetime.now() - session.last_activity > timedelta(minutes=self.timeout_minutes):
                session.is_active = False
                return None
            session.update_activity()
            return session
        return None

    def end_session(self, session_id: str) -> bool:
        """End a session"""
        session = self.sessions.get(session_id)
        if session:
            session.is_active = False
            return True
        return False

    def cleanup_expired(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired = [
            sid for sid, session in self.sessions.items()
            if not session.is_active or 
            (now - session.last_activity).total_seconds() > self.timeout_minutes * 60
        ]
        for sid in expired:
            del self.sessions[sid]

