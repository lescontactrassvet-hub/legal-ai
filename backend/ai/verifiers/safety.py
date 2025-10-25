"""
Safety verifier module for filtering unsafe or sensitive content.
"""

import re
from typing import Any

class SafetyVerifier:
    """
    Verifies that the generated content meets basic safety criteria:
    - content is a string
    - does not exceed maximum length
    - does not contain long sequences of digits
    """

    def __init__(self, max_digits: int = 6, max_length: int = 5000) -> None:
        self.max_digits = max_digits
        self.max_length = max_length
        # Compile a pattern to detect sequences of digits longer than max_digits
        self._digit_pattern = re.compile(r"\d{" + str(self.max_digits) + ",}")

    def verify(self, content: Any) -> bool:
        """
        Verify that the content is safe.

        Args:
            content: The generated content to validate.

        Returns:
            True if content is safe, False otherwise.
        """
        # Content must be a string
        if not isinstance(content, str):
            return False
        # Content length must not exceed the max_length threshold
        if len(content) > self.max_length:
            return False
        # Check for long sequences of digits (e.g., potential personal data)
        if self._digit_pattern.search(content):
            return False
        return True
