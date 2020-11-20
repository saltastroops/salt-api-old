"""User roles relevant for authorization."""
from saltapi.repository.user_repository import User


def has_role(user: User, role: str) -> bool:
    """Check whether the user has a role."""
    return False
