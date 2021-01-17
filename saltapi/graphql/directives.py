"""GraphQL schema directives."""
import logging
from typing import Any, Union

from ariadne import SchemaDirectiveVisitor
from graphql import (
    GraphQLField,
    GraphQLInterfaceType,
    GraphQLObjectType,
    default_field_resolver,
)

from saltapi.auth import authorization
from saltapi.auth.authorization import Permission, Role

logger = logging.getLogger(__name__)


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
            roles = [Role.from_name(r) for r in self.args.get("roles")]
            permissions = [
                Permission.from_name(p) for p in self.args.get("permissions")
            ]
            user = args[1].context["request"].user
            auth = args[1].context["request"].auth

            if not authorization.has_any_of_roles_or_permissions(
                user=user, auth=auth, roles=roles, permissions=permissions, **kwargs
            ):
                logger.info(msg="Not authorized")
                raise Exception("Not authorized.")

            return await original_resolver(*args, **kwargs)

        field.resolve = new_resolver
        return field
