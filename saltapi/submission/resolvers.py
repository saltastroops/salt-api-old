"""Resolvers for submitting content."""
from typing import Any, Optional

from ariadne import convert_kwargs_to_snake_case
from starlette.datastructures import UploadFile


@convert_kwargs_to_snake_case
def resolve_submit_proposal(
    root: Any, info: Any, proposal: UploadFile, proposal_code: Optional[str] = None
) -> str:
    """Submit a proposal."""
    return "43"
