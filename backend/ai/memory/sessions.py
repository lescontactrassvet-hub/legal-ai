"""
Session management for AI conversations.

This module defines classes to manage dialogue sessions and contexts
for the AI consultant, storing user history and state across messages.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

class Session:
    """
    Represents an individual dialogue session.
    """

    def __init__(self, session_id: Optional[str] = None) -> None:
        self.session_id: str = session_id or str(uuid.uuid4())
        self.created_at: datetime = datetime.utcnow()
        self.messages: List[Dict[str, Any]] = []

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the session history.

        Parameters:
            role (str): The role of the speaker, e.g., 'user' or 'assistant'.
            content (str): The content of the message.
        """
        self.messages.append({"role": role, "content": content})


class SessionManager:
    """
    In-memory session manager to track multiple sessions.
    """

    def __init__(self) -> None:
        self.sessions: Dict[str, Session] = {}

    def get_session(self, session_id: Optional[str] = None) -> Session:
        """
        Retrieve an existing session or create a new one if session_id is None or does not exist.

        Parameters:
            session_id (Optional[str]): Optional session identifier.

        Returns:
            Session: The retrieved or newly created session.
        """
        if session_id is None or session_id not in self.sessions:
            session = Session(session_id)
            self.sessions[session.session_id] = session
            return session
        return self.sessions[session_id]
