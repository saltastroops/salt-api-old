"""User roles relevant for authorization."""
import enum
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
from saltapi.repository.user_repository import User, is_user_pc, is_user_pi, is_user_verified


class Permission(enum.Enum):
    """A permission."""

    SUBMIT_PROPOSAL = "SUBMIT_PROPOSAL"
    VIEW_PROPOSAL = "VIEW_PROPOSAL"

    @staticmethod
    def from_name(name: str) -> "Permission":
        """Return the permission for a name."""
        for _name, member in Permission.__members__.items():
            if _name == name:
                return member
        raise ValueError(f"Unknown permission: {name}")


class Role(enum.Enum):
    """A role."""

    ADMINISTRATOR = "ADMINISTRATOR"

    @staticmethod
    def from_name(name: str) -> "Role":
        """Return the permission for a name."""
        for _name, member in Role.__members__.items():
            if _name == name:
                return member
        raise ValueError(f"Unknown role: {name}")


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
            return

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


def has_permission(user: User, permission: Permission) -> bool:
    """Check whether the user has a role."""
    if permission in user.permissions:
        return True
    return False


def can_submit_proposal(user: User, proposal_code: Optional[str] = None) -> None:
    """
    Check whether a user can submit a proposal.

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
    if not is_user_verified:
        raise Exception("User not verified.8")
    if not proposal_code:  # Is a new proposal
        return
    if is_user_pi(user.username, proposal_code):  # User is a principal investigator
        return
    if is_user_pc(user.username, proposal_code):  # User is a principal contact
        return
    raise Exception("Only the Principal Investigator and Principal Contact may resubmit a proposal.")
