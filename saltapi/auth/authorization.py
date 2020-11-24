"""User roles relevant for authorization."""
from typing import Any, List, Optional, Tuple

from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
)
from starlette.requests import HTTPConnection

from saltapi.auth.token import parse_token
from saltapi.repository import user_repository
from saltapi.repository.user_repository import User, is_user_pc, is_user_pi

# authentication


class AuthenticatedUser(BaseUser):
    """An authenticated user."""

    def __init__(self, user: user_repository.User):
        self.user = user

    @property
    def is_authenticated(self) -> bool:
        """Return True."""
        return True

    @property
    def display_name(self) -> str:
        """Return the user's full name."""
        return f"{self.user.first_name} {self.user.last_name}"

    def __getattr__(self, item: Any) -> Any:
        """Return the same attribute of the underlying User instance."""
        return self.user.__getattribute__(item)


class TokenAuthenticationBackend(AuthenticationBackend):
    """
    Authentication backend for token-based authentication.

    The token must be sent in the Authorization HTTP header:

    Authorization: Bearer <token>
    """

    async def authenticate(
        self, request: HTTPConnection
    ) -> Optional[Tuple[AuthCredentials, BaseUser]]:
        """Authenticate the user."""
        if "Authorization" not in request.headers:
            if "token" == str(request.url).split("/")[-1]:
                return None
            raise AuthenticationError("Authorization header missing.")

        authorization_header = request.headers["Authorization"]
        if not authorization_header.startswith("Bearer "):
            raise AuthenticationError(
                "Invalid Authorization header value. The header "
                "value must have the format Bearer <token>."
            )

        user_token = request.headers["Authorization"][7:]  # length of "Bearer " is 7
        try:
            payload = parse_token(user_token)
        except Exception:
            raise AuthenticationError("Invalid or expired authentication token.")

        user = await user_repository.find_user_by_id(int(payload.user_id))

        if not user:
            raise AuthenticationError("No user found for user id.")

        return AuthCredentials(["authenticated"]), AuthenticatedUser(user)


def has_role(user: User, role: str) -> bool:
    """Check whether the user has a role."""
    return False


def has_any_of_roles_or_permissions(
    user: User, auth: AuthCredentials, roles: List[str], permissions: List[str]
) -> bool:
    """Check whether the user has any of a list of roles and permissions."""
    for permission in permissions:
        if permission in auth.scopes:
            return True

    for role in roles:
        if has_role(user, role):
            return True

    return False


def can_re_submit_proposal(proposal_code: str, username: str):
    """
    Check whether a user can resubmit a proposal.

    Parameters
    ----------
    proposal_code
        The proposal code
    username
        The PIPT username

    Returns
    -------
    True
        If the the user can re submit the proposal.

    """
    if is_user_pi(username, proposal_code):
        return True
    if is_user_pc(username, proposal_code):
        return True
    return False
