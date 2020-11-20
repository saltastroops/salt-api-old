"""Non-GraphQL routes for the server."""
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from saltapi.auth import create_token
from saltapi.util.error import UsageError


class Credentials(BaseModel):
    """Authentication credentials."""

    username: str
    password: str


async def token(request: Request) -> Response:
    """Request an authentication token."""
    body = await request.json()
    credentials = Credentials(**body)

    try:
        auth_token = await create_token(
            username=credentials.username, password=credentials.password
        )
        return JSONResponse({"token": auth_token})
    except ValueError:
        raise UsageError("Invalid username or password.", 401)
