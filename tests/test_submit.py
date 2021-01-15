"""Tests for submitting."""
from io import BytesIO
from typing import Any

from starlette.testclient import TestClient

from saltapi.app import app


def test_no_submission_without_authorisation(authuser: Any):
    """Submission should not be possible if the user is not authorised."""
    client = TestClient(app)

    def submit_proposal(proposal_code):
        return True

    authuser.is_permitted_to.set(submit_proposal)
    response = client.post(
        "/graphql/",
        data={
            "operations": '{ "query": "mutation ($file: Upload!) { submitProposal(proposal: $file, proposalCode: \\"2020-1-SCI-042\\") }", "variables": { "file": null } }',  # noqa
            "map": '{ "0": ["variables.file"] }',
        },
        files={"0": ("proposal", BytesIO(), "application/zip")},
    )
    assert response.status_code == 789


# @pytest.mark.asyncio
# async def test_submit_proposal_with_response_that_cannot_be_parsed(
#     monkeypatch, httpx_mock: HTTPXMock
# ):
#     """Test submitting a proposal with a response that cannot be parsed."""
#     monkeypatch.setattr(resolvers, "username", lambda info: "someone")
#     httpx_mock.add_response(
#         url=proposal_submission_url,
#         method="POST",
#         status_code=422,
#         data="A field is missing.",
#     )
#     proposal = UploadFile(filename="proposal.zip", file=BytesIO())
#     with pytest.raises(Exception) as excinfo:
#         await resolvers.resolve_submit_proposal({}, {}, proposal=proposal)
#     assert "storage service" in str(excinfo.value)
#
#
# @pytest.mark.asyncio
# async def test_submit_proposal_with_error_response(monkeypatch,
# httpx_mock: HTTPXMock):
#     """Test submitting a proposal with an error response."""
#     monkeypatch.setattr(resolvers, "username", lambda info: "someone")
#     error = "The server is having a tea break"
#     httpx_mock.add_response(
#         url=proposal_submission_url,
#         method="POST",
#         json={"error": error},
#     )
#     proposal = UploadFile(filename="proposal.zip", file=BytesIO())
#     with pytest.raises(Exception) as excinfo:
#         await resolvers.resolve_submit_proposal({}, {}, proposal=proposal)
#     assert str(excinfo.value) == error
#
#
# @pytest.mark.asyncio
# async def test_submit_proposal_with_submission_id_response(
#     monkeypatch, httpx_mock: HTTPXMock
# ):
#     """Test submitting a proposal with a submission id response."""
#     monkeypatch.setattr(resolvers, "username", lambda info: "someone")
#     submission_id = "67a7aded-758c-4e41-a9d3-2fd45e94c108"
#     httpx_mock.add_response(
#         url=proposal_submission_url,
#         method="POST",
#         json={"submission_id": submission_id},
#     )
#     proposal = UploadFile(filename="proposal.zip", file=BytesIO())
#     return_value = await resolvers.resolve_submit_proposal({}, {}, proposal=proposal)
#     assert return_value == submission_id
