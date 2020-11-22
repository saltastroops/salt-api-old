"""User roles relevant for authorization."""
from typing import List

from starlette.authentication import AuthCredentials

from saltapi.repository.user_repository import User


def has_role(user: User, role: str) -> bool:
    """Check whether the user has a role."""
    return False


def has_any_of_roles_or_permissions(
    user: User, auth: AuthCredentials, roles: List[str], permissions: List[str]
) -> bool:
    """Check whether the user has any of a list of roles and permissions."""
    print(user, auth, roles, permissions)
    for permission in permissions:
        if permission in auth.scopes:
            return True

    for role in roles:
        if has_role(user, role):
            return True

    return False
