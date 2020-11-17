"""Tests for custom GraphQL scalars."""

from datetime import datetime

import pytest
import pytz

from saltapi.graphql import scalars


@pytest.mark.parametrize(
    "proposal_code", ["2020-1-SCI-004", "2109-2-RSA-342", "2021-3-IUCAA_RU"]
)
def test_parse_valid_proposal_codes(proposal_code):
    """Return proposal codes as is."""
    assert scalars.parse_proposal_code(proposal_code) == proposal_code


@pytest.mark.parametrize(
    "proposal_code", ["1234-SCI-001", "Unsubmitted-002", "3009-MLT-042"]
)
def test_reject_invalid_proposal_codes(proposal_code):
    """Reject invalid proposal codes."""
    with pytest.raises(ValueError):
        scalars.parse_proposal_code(proposal_code)


@pytest.mark.parametrize(
    "t,expected",
    [
        ("2020-04-05T04:07:09.876Z", datetime(2020, 4, 5, 4, 7, 9, 876, pytz.utc)),
        ("2021-08-06T23:13:14-07", datetime(2021, 8, 7, 6, 13, 14, 0, pytz.utc)),
        ("2021-08-06T12:13:14+05", datetime(2021, 8, 6, 7, 13, 14, 0, pytz.utc)),
    ],
)
def test_parse_valid_datetimes(t, expected):
    """Parse valid datetimes correctly."""
    assert abs(scalars.parse_datetime(t) - expected).seconds < 0.1


@pytest.mark.parametrize("t", ["2020", "2020-01-05T12:09:08", "today"])
def test_reject_invalid_datetimes(t):
    """Reject invalid datetimes and datetimes without a timezone."""
    with pytest.raises(ValueError):
        scalars.parse_datetime(t)


@pytest.mark.parametrize(
    "t",
    [
        datetime(2022, 11, 9, 7, 12, 4, tzinfo=pytz.timezone("UTC")),
        datetime(2023, 7, 2, tzinfo=pytz.timezone("Africa/Johannesburg")),
    ],
)
def test_serialize_valid_datetimes(t):
    """Serialize valid datetimes correctly."""
    serialized_and_parsed = scalars.parse_datetime(scalars.serialize_datetime(t))
    assert abs(serialized_and_parsed - t).seconds < 0.1


def test_reject_naive_datetimes():
    """Reject naive datetimes when serializing."""
    t = datetime(2020, 8, 7, 4, 7, 3, 4)
    with pytest.raises(ValueError):
        scalars.serialize_datetime(t)
