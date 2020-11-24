"""Create and parse authentication tokens."""
import dataclasses
import os

import jwt

from saltapi.repository import user_repository
from saltapi.util.error import UsageError


@dataclasses.dataclass(frozen=True)
class TokenPayload:
    """The payload of an authentication token."""

    user_id: str


async def create_token(username: str, password: str) -> str:
    """
    Create an authentication token.

    An exception is raised if the username or password are invalid.
    """
    user = await user_repository.find_user_by_credentials(username, password)
    if not user:
        raise ValueError("Invalid username or password.")
    return jwt.encode(
        {"user_id": f"{user.id}"}, os.environ["SECRET_TOKEN_KEY"], algorithm="HS256"
    ).decode("utf-8")


def parse_token(token: str) -> TokenPayload:
    """
    Parse a token and return its payload.

    An exception is raised if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, os.environ["SECRET_TOKEN_KEY"], algorithms=["HS256"]
        )
        return TokenPayload(user_id=payload["user_id"])
    except jwt.ExpiredSignatureError:
        raise UsageError("the authentication token has expired.")
    except Exception:
        raise UsageError("Invalid authentication token.")
