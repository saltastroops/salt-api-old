"""The server for the SALT API."""
import pathlib
from typing import Any, Dict, Optional, Tuple

import dotenv
from ariadne import MutationType, load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
)
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection, Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from saltapi import routes
from saltapi.auth.token import parse_token
from saltapi.graphql import resolvers
from saltapi.graphql.directives import PermittedForDirective
from saltapi.repository import user_repository
from saltapi.repository.database import database
from saltapi.util.error import UsageError

dotenv.load_dotenv()

# authentication


class AuthenticatedUser(BaseUser):
    """An authenticated user."""

    def __init__(self, user: user_repository.User):
        self.user = user

    @property
    def is_authenticated(self) -> bool:
        """Return True."""
        return True

    @property
    def display_name(self) -> str:
        """Return the user's full name."""
        return f"{self.user.first_name} {self.user.last_name}"

    def __getattr__(self, item: Any) -> Any:
        """Return the same attribute of the underlying User instance."""
        return self.user.__getattribute__(item)


class TokenAuthenticationBackend(AuthenticationBackend):
    """
    Authentication backend for token-based authentication.

    The token must be sent in the Authorization HTTP header:

    Authorization: Bearer <token>
    """

    async def authenticate(
        self, request: HTTPConnection
    ) -> Optional[Tuple[AuthCredentials, BaseUser]]:
        """Authenticate the user."""
        if "Authorization" not in request.headers:
            return None

        authorization_header = request.headers["Authorization"]
        if not authorization_header.startswith("Bearer "):
            raise AuthenticationError(
                "Invalid Authorization header value. The header "
                "value must have the format Bearer <token>."
            )

        user_token = request.headers["Authorization"][7:]  # length of "Bearer " is 7
        try:
            payload = parse_token(user_token)
        except Exception:
            raise AuthenticationError("Invalid or expired authentication token.")

        user = await user_repository.find_user_by_id(int(payload.user_id))

        if not user:
            raise AuthenticationError("No user found for user id.")

        return AuthCredentials(["authenticated"]), AuthenticatedUser(user)


# error handling


def error_response(detail: str, status_code: int) -> Response:
    """JSON response returned for an error."""
    return JSONResponse({"detail": detail}, status_code=status_code)


async def http_exception(request: Request, e: HTTPException) -> Response:
    """Handle a HTTPException."""
    return error_response(e.detail, e.status_code)


async def usage_error(request: Request, e: UsageError) -> Response:
    """Handle a user error."""
    return error_response(str(e), e.status_code)


async def validation_error(request: Request, e: ValidationError) -> Response:
    """Handle a validation error raised by pydantic."""
    return error_response(str(e), 400)


exception_handlers: Dict[Any, Any] = {
    HTTPException: http_exception,
    UsageError: usage_error,
    ValidationError: validation_error,
}


# middleware

middleware = [
    Middleware(AuthenticationMiddleware, backend=TokenAuthenticationBackend())
]


# GraphQL

schema_path = (
    pathlib.Path(__file__).parent.absolute().joinpath("graphql", "schema.graphql")
)
type_defs = load_schema_from_path("saltapi/graphql/schema.graphql")

mutation = MutationType()
mutation.set_field("submitProposal", resolvers.resolve_submit_proposal)

schema = make_executable_schema(
    type_defs, mutation, directives={"permittedFor": PermittedForDirective}
)


# non-GraphQL routes


async def token(request: Request) -> Response:
    """Request an authentication token."""
    return await routes.token(request)


async def public_key(request: Request) -> Response:
    """Request the public key for token authentication."""
    return await routes.public_key(request)


non_graphql_routes = [
    Route("/token", token, methods=["POST"]),
    Route("/public-key", public_key, methods=["GET"]),
]


# create the app

app = Starlette(
    middleware=middleware,
    exception_handlers=exception_handlers,
    routes=non_graphql_routes,
    on_startup=[database.connect],
    on_shutdown=[database.disconnect],
)
app.mount("/graphql", GraphQL(schema))
