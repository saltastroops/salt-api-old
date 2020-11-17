"""Resolvers for submitting content."""

from ariadne import convert_kwargs_to_snake_case


@convert_kwargs_to_snake_case
def resolve_submit_proposal(root, info, proposal=None, proposal_code=None):
    """Submit a proposal."""
    return "43"
