"""The server for the SALT API."""
import pathlib
import typing

from ariadne import MutationType, load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL
from starlette.applications import Starlette
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    BaseUser,
    SimpleUser, AuthenticationError, requires,
)
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from starlette.responses import JSONResponse
from starlette.routing import Route

from saltapi.authenticate import login_user, validate_token, get_user_id_from_token
from saltapi.graphql.directives import PermittedForDirective
from saltapi.repository.database import sdb_connection
from saltapi.repository.user_repository import find_user_by_id
from saltapi.submission.resolvers import resolve_submit_proposal


class TokenAuthentication(AuthenticationBackend):
    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return

        user_token = request.headers["Authorization"]
        try:
            validate_token(user_token)
        except ValueError as exc:
            raise AuthenticationError('Invalid user token.')

        user_id = get_user_id_from_token(user_token)
        user = await find_user_by_id(user_id)
        username = user["username"]

        return AuthCredentials(["authenticated"]), user


async def token(request):
    return await login_user(request)


@requires('authenticated')
async def user(request):
    return JSONResponse(request.user)


middleware = [Middleware(AuthenticationMiddleware, backend=TokenAuthentication())]

schema_path = (
    pathlib.Path(__file__).parent.absolute().joinpath("graphql", "schema.graphql")
)
type_defs = load_schema_from_path("saltapi/graphql/schema.graphql")

mutation = MutationType()
mutation.set_field("submitProposal", resolve_submit_proposal)

schema = make_executable_schema(
    type_defs, mutation, directives={"permittedFor": PermittedForDirective}
)

app = Starlette(
    middleware=middleware,
    debug=True,
    routes=[
        Route('/token', token, methods=['POST']),
        Route('/user', user, methods=['GET'])
    ],
    on_startup=[sdb_connection.connect],
    on_shutdown=[sdb_connection.disconnect]
)
app.mount("/", GraphQL(schema))

