"""The server for the SALT API."""

from ariadne import load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL
from starlette.applications import Starlette

type_defs = load_schema_from_path("saltapi/schema.graphql")

schema = make_executable_schema(type_defs)

app = Starlette()
app.mount("/", GraphQL(schema))
