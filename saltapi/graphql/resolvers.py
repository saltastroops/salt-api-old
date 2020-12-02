"""Resolvers for submitting content."""
import asyncio
from typing import Any, Optional

from ariadne import convert_kwargs_to_snake_case
from starlette.datastructures import UploadFile

from saltapi.auth.authorization import can_submit_proposal
from saltapi.repository.submission_repository import (
    SubmissionStatus,
    find_submission_log_entries,
    find_submission_status,
)
from saltapi.submission.submit import submit_proposal


def username(info: Any) -> str:
    """Return the username of the authenticated user."""
    return str(info.context["request"].user.username)


@convert_kwargs_to_snake_case
async def resolve_submit_proposal(
    root: Any, info: Any, proposal: UploadFile, proposal_code: Optional[str] = None
) -> str:
    """Submit a proposal."""
    user = info.context["request"].user
    can_submit_proposal(user.username, proposal_code)

    return await submit_proposal(
        proposal=proposal,
        proposal_code=proposal_code,
        submitter=user,
    )


@convert_kwargs_to_snake_case
async def submission_progress_generator(root: Any, info: Any, submission_id: str):
    """Generate content for the submission progress resolver."""
    latest_entry_number = 0
    previous_status: Optional[SubmissionStatus] = None
    while True:
        log_entries = await find_submission_log_entries(
            submission_id, latest_entry_number
        )
        status = await find_submission_status(submission_id)
        if len(log_entries):
            latest_entry_number = log_entries[-1].entry_number

        progress = {
            "submissionId": submission_id,
            "logEntries": [
                {
                    "messageType": le.message_type.name,
                    "message": le.message,
                    "timestamp": le.logged_at,
                }
                for le in log_entries
            ],
            "status": status.name,
        }

        if status != previous_status or len(log_entries):
            yield progress

        if status in [
            SubmissionStatus.FAILED,
            SubmissionStatus.SUCCESSFUL,
        ]:
            return

        previous_status = status

        await asyncio.sleep(5)


@convert_kwargs_to_snake_case
def resolve_submission_progress(progress: Any, info: Any, submission_id: str):
    """Return the progress details."""
    return progress
