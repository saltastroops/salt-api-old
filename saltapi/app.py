"""The server for the SALT API."""
import os

from ariadne import load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL
from starlette.applications import Starlette
from starlette.routing import Route

from saltapi.auth.login import login_user

type_defs = load_schema_from_path("saltapi/graphql/schema.graphql")

schema = make_executable_schema(type_defs)

app = Starlette()
app.mount("/", GraphQL(schema))


async def login(request):
    return login_user(request)


app = Starlette(debug=True, routes=[
    Route('/login', login, methods=['POST']),
])
