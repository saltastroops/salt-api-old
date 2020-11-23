"""Non-GraphQL routes for the server."""
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

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
    auth_token = await create_token(user=user)
    return JSONResponse({"token": auth_token})
