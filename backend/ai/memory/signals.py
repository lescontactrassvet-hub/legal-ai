"""
Signal processing and feedback mechanisms for AI interactions.

This module defines structures to handle feedback signals such as user ratings,
clarification requests, and active learning triggers to improve the AI consultant.
"""

from typing import Any, Dict, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class FeedbackSignal:
    """
    Represents a feedback signal from a user.
    """
    session_id: str
    timestamp: datetime
    signal_type: str  # e.g., 'like', 'dislike', 'clarification'
    payload: Dict[str, Any] = field(default_factory=dict)


class SignalManager:
    """
    Collects and stores feedback signals for analysis and training.
    """

    def __init__(self) -> None:
        self.signals: List[FeedbackSignal] = []

    def record_signal(self, signal: FeedbackSignal) -> None:
        """
        Record a feedback signal.

        Parameters:
            signal (FeedbackSignal): The feedback signal to record.
        """
        self.signals.append(signal)
