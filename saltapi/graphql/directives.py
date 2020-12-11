"""GraphQL schema directives."""

from typing import Any, Union

from ariadne import SchemaDirectiveVisitor
from graphql import (
    GraphQLField,
    GraphQLInterfaceType,
    GraphQLObjectType,
    default_field_resolver,
)


class AuthenticatedDirective(SchemaDirectiveVisitor):
    """Directive for checking if user is authenticated."""

    def visit_field_definition(
        self,
        field: GraphQLField,
        object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ) -> GraphQLField:
        """Check authorization and execute query."""
        original_resolver = field.resolve or default_field_resolver

        async def new_resolver(*args: Any, **kwargs: Any) -> Any:
            if not args[1].context["request"].user.is_authenticated:
                raise Exception("User is not authenticated.")

            return await original_resolver(*args, **kwargs)

        field.resolve = new_resolver
        return field
