"""Parsers and serializers for custom GraphQL types."""

from datetime import datetime

from dateutil import parser


def serialize_proposal_code(proposal_code: str) -> str:
    """Serialize a proposal code value."""
    return str(proposal_code)


def parse_proposal_code(proposal_code: str) -> str:
    """Parse a proposal code value."""
    if not proposal_code.startswith("2"):
        raise ValueError("Invalid proposal code.")
    return str(proposal_code)


def serialize_datetime(t: datetime) -> str:
    """
    Serialize a datetime to an ISO 8601 string.

    The datetime must be timezone-aware.
    """
    if t.tzinfo is None or t.tzinfo.utcoffset(t) is None:
        raise ValueError("The datetime must be timezone-aware.")
    return t.isoformat()


def parse_datetime(t: str) -> datetime:
    """Parse a string as a datetime in ISO 8601 format."""
    parsed = parser.isoparse(t)
    if parsed.tzinfo is None or parsed.tzinfo.utcoffset(t) is None:
        raise ValueError("The datetime is missing timezone information.")
    return parsed
