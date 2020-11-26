"""Database access for submission related content."""
import dataclasses
import enum
import os
from datetime import datetime
from typing import List

from pytz import timezone

from saltapi.repository.database import database


class SubmissionStatus(enum.Enum):
    """A submission status."""

    FAILED = "Failed"
    IN_PROGRESS = "In Progress"
    SUCCESSFUL = "Successful"

    @staticmethod
    def from_value(value: str) -> "SubmissionStatus":
        """Return the SubmissionStatus with a given value."""
        for status in SubmissionStatus:
            if status.value == value:
                return status
        raise ValueError(f"Unknown submission status value: {value}")


class LogMessageType(enum.Enum):
    """A log message type."""

    ERROR = "Error"
    INFO = "Info"
    WARNING = "Warning"

    @staticmethod
    def from_value(value: str) -> "LogMessageType":
        """Return the LogMessageType with a given value."""
        for lmt in LogMessageType:
            if lmt.value == value:
                return lmt
        raise ValueError(f"Unknown log message type value: {value}")


@dataclasses.dataclass(frozen=True)
class SubmissionLogEntry:
    """An entry in a submission log."""

    submission_identifier: str
    entry_number: int
    message_type: LogMessageType
    message: str
    logged_at: datetime


async def find_submission_status(submission_identifier: str) -> SubmissionStatus:
    """Get the current status of a submission."""
    query = """
SELECT SubmissionStatus
FROM SubmissionStatus status
JOIN Submission s ON status.SubmissionStatus_Id=s.SubmissionStatus_Id
WHERE s.Identifier = :identifier
    """
    values = {"identifier": submission_identifier}
    row = await database.fetch_one(query=query, values=values)
    if not row:
        raise ValueError(f"Unknown submission identifier: {submission_identifier}")
    return SubmissionStatus.from_value(row[0])


async def find_submission_log_entries(
    submission_identifier: str,
    skip: int,
) -> List[SubmissionLogEntry]:
    """Get the entries in the submission log for a submission."""
    query = """
SELECT SubmissionLogEntryNumber, SubmissionMessageType, Message, LoggedAt
FROM SubmissionLogEntry sle
JOIN Submission s ON sle.Submission_Id = s.Submission_Id
JOIN SubmissionMessageType smt
               ON sle.SubmissionMessageType_Id = smt.SubmissionMessageType_Id
WHERE s.Identifier = :identifier
ORDER BY sle.SubmissionLogEntryNumber
LIMIT :skip, 100000
    """
    values = {"identifier": submission_identifier, "skip": skip}
    rows = await database.fetch_all(query=query, values=values)
    database_timezone = timezone(os.environ["DATABASE_TIMEZONE"])
    return [
        SubmissionLogEntry(
            submission_identifier=submission_identifier,
            entry_number=row[0],
            message_type=LogMessageType.from_value(row[1]),
            message=row[2],
            logged_at=database_timezone.localize(row[3]),
        )
        for row in rows
    ]
