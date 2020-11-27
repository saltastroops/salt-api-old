"""GraphQL schema directives."""

from typing import Any, Union

from ariadne import SchemaDirectiveVisitor
from graphql import (
    GraphQLField,
    GraphQLInterfaceType,
    GraphQLObjectType,
    default_field_resolver,
)
from saltapi.auth.authorization import (
    Permission,
    Role,
    can_submit_proposal,
    has_any_of_roles_or_permissions
)


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

            proposal_code = kwargs["proposalCode"] if "proposalCode" in kwargs else None
            if (
                    (args[1].path.key == "submitProposal" or args[1].path.key == "submitBlock")
                    and can_submit_proposal(user.username, proposal_code)
            ):
                return await original_resolver(*args, **kwargs)

            if not has_any_of_roles_or_permissions(
                user=user, auth=auth, roles=roles, permissions=permissions, **kwargs
            ):
                raise Exception("Not authorized.")

            return await original_resolver(*args, **kwargs)

        field.resolve = new_resolver
        return field
