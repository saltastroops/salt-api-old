"""GraphQL schema directives."""

from typing import Any, Union

from ariadne import SchemaDirectiveVisitor
from graphql import (
    GraphQLField,
    GraphQLInterfaceType,
    GraphQLObjectType,
    default_field_resolver,
)

from saltapi.auth.roles import has_role


class PermittedForDirective(SchemaDirectiveVisitor):
    """Directive for handling permissions."""

    def visit_field_definition(
        self,
        field: GraphQLField,
        object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ) -> GraphQLField:
        """Check authorization and execute query."""
        original_resolver = field.resolve or default_field_resolver

        async def new_resolver(*args: Any, **kwargs: Any) -> Any:
            roles = self.args.get("roles")
            permissions = self.args.get("permissions")
            user = args[1].context["request"].user
            auth = args[1].context["request"].auth

            # May the user make the query because they have the permission?
            authorized = False
            for permission in permissions:
                if permission in auth.scopes:
                    authorized = True
                    break

            # May the user make the query because they have a role permitting it?
            for role in roles:
                if has_role(user, role):
                    authorized = True
                    break

            if not authorized:
                raise Exception("Not authorized.")

            return original_resolver(*args, **kwargs)

        field.resolve = new_resolver
        return field
