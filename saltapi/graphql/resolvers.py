"""Resolvers for submitting content."""
from typing import Any, Optional

from ariadne import convert_kwargs_to_snake_case
from starlette.datastructures import UploadFile

from saltapi.submission.submit import submit_proposal


def username(info: Any) -> str:
    """Return the username of the authenticated user."""
    return str(info.context["request"].user.username)


@convert_kwargs_to_snake_case
async def resolve_submit_proposal(
    root: Any, info: Any, proposal: UploadFile, proposal_code: Optional[str] = None
) -> str:
    """Submit a proposal."""
    return await submit_proposal(
        proposal=proposal,
        proposal_code=proposal_code,
        submitter=username(info),
    )
