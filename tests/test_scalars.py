"""Tests for custom GraphQL scalars."""

import pytest

from saltapi.graphql import scalars


@pytest.mark.parametrize(
    "proposal_code", [("2020-1-SCI-004"), ("2109-2-RSA-342"), ("2021-3-IUCAA_RU")]
)
def test_parse_valid_proposal_codes(proposal_code):
    """Return proposal codes as is."""
    assert scalars.parse_proposal_code(proposal_code) == proposal_code


@pytest.mark.parametrize(
    "proposal_code", [("1234-SCI-001"), ("Unsubmitted-002"), ("3009-MLT-042")]
)
def test_reject_invalid_proposal_codes(proposal_code):
    """Reject invalid proposal codes."""
    with pytest.raises(ValueError):
        scalars.parse_proposal_code(proposal_code)
