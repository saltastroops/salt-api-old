"""Parsers and serializers for custom GraphQL types."""


def serialize_proposal_code(proposal_code: str) -> str:
    """Serialize a proposal code value."""
    return str(proposal_code)


def parse_proposal_code(proposal_code: str) -> str:
    """Parse a proposal code value."""
    if not proposal_code.startswith("2"):
        raise ValueError("Invalid proposal code.")
    return str(proposal_code)
