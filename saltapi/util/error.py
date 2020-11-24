"""Custom exceptions."""
from typing import Dict


class UsageError(Exception):
    """An exception indicating a user error."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

    def to_dict(self) -> Dict[str, str]:
        """Convert the exception to a dictionary."""
        return dict(message=self.message)
