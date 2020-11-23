"""Non-GraphQL routes for the server."""
import os

from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response

from saltapi.auth.token import create_token
from saltapi.repository import user_repository
from saltapi.util.error import UsageError


class Credentials(BaseModel):
    """Authentication credentials."""

    username: str
    password: str


async def token(request: Request) -> Response:
    """Request an authentication token."""
    body = await request.json()
    credentials = Credentials(**body)

    username = credentials.username
    password = credentials.password
    user = await user_repository.find_user_by_credentials(username, password)
    if not user:
        raise UsageError("Invalid username or password.", 401)
    auth_token = create_token(user=user)
    return JSONResponse({"token": auth_token})


async def public_key(request: Request) -> Response:
    """Return the public key for signing with the RS256 algorithm."""
    with open(os.environ["RS256_PUBLIC_KEY_FILE"]) as f:
        key = f.read()
    return PlainTextResponse(key)
