"""Tests for submitting."""
from io import BytesIO

import pytest
from pytest_httpx import HTTPXMock
from starlette.datastructures import UploadFile

from saltapi.graphql import resolvers
from saltapi.submission.submit import proposal_submission_url


@pytest.mark.asyncio
async def test_submit_proposal_with_response_that_cannot_be_parsed(
    monkeypatch, httpx_mock: HTTPXMock
):
    """Test submitting a proposal with a response that cannot be parsed."""
    monkeypatch.setattr(resolvers, "username", lambda info: "someone")
    httpx_mock.add_response(
        url=proposal_submission_url,
        method="POST",
        status_code=422,
        data="A field is missing.",
    )
    proposal = UploadFile(filename="proposal.zip", file=BytesIO())
    with pytest.raises(Exception) as excinfo:
        await resolvers.resolve_submit_proposal({}, {}, proposal=proposal)
    assert "storage service" in str(excinfo.value)


@pytest.mark.asyncio
async def test_submit_proposal_with_error_response(monkeypatch, httpx_mock: HTTPXMock):
    """Test submitting a proposal with an error response."""
    monkeypatch.setattr(resolvers, "username", lambda info: "someone")
    error = "The server is having a tea break"
    httpx_mock.add_response(
        url=proposal_submission_url,
        method="POST",
        json={"error": error},
    )
    proposal = UploadFile(filename="proposal.zip", file=BytesIO())
    with pytest.raises(Exception) as excinfo:
        await resolvers.resolve_submit_proposal({}, {}, proposal=proposal)
    assert str(excinfo.value) == error


@pytest.mark.asyncio
async def test_submit_proposal_with_submission_id_response(
    monkeypatch, httpx_mock: HTTPXMock
):
    """Test submitting a proposal with a submission id response."""
    monkeypatch.setattr(resolvers, "username", lambda info: "someone")
    submission_id = "67a7aded-758c-4e41-a9d3-2fd45e94c108"
    httpx_mock.add_response(
        url=proposal_submission_url,
        method="POST",
        json={"submission_id": submission_id},
    )
    proposal = UploadFile(filename="proposal.zip", file=BytesIO())
    return_value = await resolvers.resolve_submit_proposal({}, {}, proposal=proposal)
    assert return_value == submission_id
