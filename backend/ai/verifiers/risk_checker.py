"""
Risk checker module.

Provides RiskChecker class that identifies potential legal and business risks
in documents or queries by scanning for known risk terms and patterns.
"""

from typing import List, Dict, Any

class RiskChecker:
    """
    Performs risk analysis on extracted text or queries.
    """

    def __init__(self, risk_terms: List[str] | None = None) -> None:
        """
        Initialize risk checker.

        Args:
            risk_terms: Optional list of terms indicating potential risks.
        """
        self.risk_terms = risk_terms or [
            "штраф", "penalty", "неустойка", "ответственность", "риск", "санкция",
            "разрыв договора", "убытки"
        ]

    def analyze(self, content: str) -> Dict[str, Any]:
        """
        Analyze content and return dict with risk indicators.

        Args:
            content: Text to analyze.

        Returns:
            Dictionary with keys:
            - "risks": list of terms found indicating risk.
            - "has_risk": bool indicating whether any risk terms were found.
        """
        found_terms = [term for term in self.risk_terms if term.lower() in content.lower()]
        return {
            "risks": found_terms,
            "has_risk": bool(found_terms),
        }
