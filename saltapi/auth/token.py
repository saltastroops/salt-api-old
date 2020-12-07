"""Create and parse authentication tokens."""
import dataclasses
import os
from time import time
from typing import List, Optional
import logging
import sys

import jwt

from saltapi.repository.user_repository import User
from saltapi.util.error import UsageError
from saltapi.repository.logging_errors import setup_logging


info_log = setup_logging(
    "info_logger",
    "saltapi_info.log",
    logging.Formatter("%(asctime)s [%(levelname)s]:[%(filename)s, line %(lineno)d]. %(message)s.", '%Y/%m/%d %H:%M:%S'),
)
error_log = setup_logging(
    "error_logger",
    "saltapi_error.log",
    logging.Formatter("%(asctime)s [%(levelname)s]: [%(filename)s, line %(lineno)d]. %(message)s.",
                      '%Y/%m/%d %H:%M:%S'),
)


@dataclasses.dataclass(frozen=True)
class TokenPayload:
    """The payload of an authentication token."""

    user_id: int
    roles: List[str]


def create_token(
    user: User, expiry: Optional[int] = None, algorithm: str = "HS256"
) -> str:
    """
    Create an authentication token.

    Use the expiry argument to the set the time in seconds after which the token
    expires. By default the token never expires.

    The algorithm must be HS256 or RS256.
    """
    payload = {"user_id": user.id, "roles": user.roles}
    if expiry:
        payload["exp"] = time() + expiry
    if algorithm == "HS256":
        key = os.environ["HS256_SECRET_KEY"]
    elif algorithm == "RS256":
        with open(os.environ["RS256_SECRET_KEY_FILE"]) as f:
            key = f.read()
    else:
        info_log.info(msg=f"Unsupported algorithm: {algorithm}")
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    return jwt.encode(payload, key, algorithm=algorithm).decode("utf-8")


def parse_token(token: str, algorithm: str = "HS256") -> TokenPayload:
    """
    Parse a token and return its payload.

    The algorithm must be HS256 or RS256.

    An exception is raised if the token is invalid or expired.
    """
    if algorithm == "HS256":
        key = os.environ["HS256_SECRET_KEY"]
    elif algorithm == "RS256":
        with open(os.environ["RS256_PUBLIC_KEY_FILE"]) as f:
            key = f.read()
    else:
        info_log.info(msg=f"Unsupported algorithm: {algorithm}")
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    try:
        payload = jwt.decode(token, key, algorithms=[algorithm])
        return TokenPayload(user_id=payload["user_id"], roles=payload.get("roles", []))
    except jwt.ExpiredSignatureError:
        error_log.error(msg=f"The authentication token has expired for {TokenPayload.user_id}")
        raise UsageError("The authentication token has expired.")
    except Exception:
        exc_type, value, traceback = sys.exc_info()
        error_log.error(msg=f"Failed with exception {exc_type.__name__}."
                            f" Invalid authentication token for {TokenPayload.user_id}")
        raise UsageError("Invalid authentication token.")
