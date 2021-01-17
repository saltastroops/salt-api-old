"""Parsers and serializers for custom GraphQL types."""

from datetime import datetime

from dateutil import parser
import logging

logger = logging.getLogger(__name__)


def serialize_proposal_code(proposal_code: str) -> str:
    """Serialize a proposal code value."""
    return str(proposal_code)


def parse_proposal_code(proposal_code: str) -> str:
    """Parse a proposal code value."""
    if not proposal_code.startswith("2"):
        logger.info(msg=f"Invalid proposal code")
        raise ValueError("Invalid proposal code.")
    return str(proposal_code)


def serialize_datetime(t: datetime) -> str:
    """
    Serialize a datetime to an ISO 8601 string.

    The datetime must be timezone-aware.
    """
    if t.tzinfo is None or t.tzinfo.utcoffset(t) is None:
        logger.error(msg=f"The datetime {t} must be timezone-aware.")
        raise ValueError("The datetime must be timezone-aware.")
    return t.isoformat()


def parse_datetime(t: str) -> datetime:
    """Parse a string as a datetime in ISO 8601 format."""
    parsed = parser.isoparse(t)
    if parsed.tzinfo is None or parsed.tzinfo.utcoffset(parsed) is None:
        logger.error(msg=f"The datetime {t} is missing timezone information.")
        raise ValueError("The datetime is missing timezone information.")
    return parsed
