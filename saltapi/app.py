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
    SimpleUser,
)
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection

from saltapi.graphql.directives import PermittedForDirective
from saltapi.submission.resolvers import resolve_submit_proposal


class FakeAuthBackend(AuthenticationBackend):
    """Fake authentication backend."""

    async def authenticate(
        self, conn: HTTPConnection
    ) -> typing.Optional[typing.Tuple["AuthCredentials", "BaseUser"]]:
        """Authenticate the user."""
        return AuthCredentials(["VIEW_ALL_PROPOSALS"]), SimpleUser("somebody")


middleware = [Middleware(AuthenticationMiddleware, backend=FakeAuthBackend())]

schema_path = (
    pathlib.Path(__file__).parent.absolute().joinpath("graphql", "schema.graphql")
)
type_defs = load_schema_from_path("saltapi/graphql/schema.graphql")

mutation = MutationType()
mutation.set_field("submitProposal", resolve_submit_proposal)

schema = make_executable_schema(
    type_defs, mutation, directives={"permittedFor": PermittedForDirective}
)

app = Starlette(middleware=middleware)
app.mount("/", GraphQL(schema))
