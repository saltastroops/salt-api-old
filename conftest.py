"""Pytest fixtures."""
from typing import Any, Callable, Dict

import pytest
from starlette.authentication import AuthCredentials
from starlette.requests import HTTPConnection

import saltapi.auth
from saltapi.auth.authorization import AuthenticatedUser
from saltapi.repository.user_repository import User


class MockUserRoles:
    """Mock user roles."""

    def __init__(self):
        self._roles: Dict[str, Callable[..., bool]] = {}

    def set(self, func: Callable[[str], bool]):
        """Set the function for a role."""
        self._roles[func.__name__] = func

    def __getattr__(self, item):
        """Use a previously set role function or a function returning False."""

        async def f(*args, **kwargs):
            if item in self._roles:
                return self._roles[item](*args, **kwargs)
            else:
                return False

        return f


class MockUserPermissions:
    """Mock user permissions."""

    def __init__(self):
        self._permissions: Dict[str, Callable[..., bool]] = {}

    def set(self, func: Callable[[str], bool]):
        """Set a permission function."""
        self._permissions[func.__name__] = func

    def __getattr__(self, item):
        """Use a previously set permission function or a function returning False."""

        async def f(*args, **kwargs):
            if item in self._permissions:
                return self._permissions[item](*args, **kwargs)
            else:
                return False

        return f


class MockUser(User):
    """Mock user."""

    def __init__(self):
        super().__init__(
            id=0,
            username="",
            first_name="",
            last_name="",
            email="",
            roles=[],  # TODO: get user permissions
            permissions=[],  # TODO: get user permissions
        )
        self.has_role_of = MockUserRoles()
        self.is_permitted_to = MockUserPermissions()


def mock_authenticate(user: MockUser) -> Callable[[Any, HTTPConnection], Any]:
    """Return an authenticated mock user."""

    async def f(self: Any, request: HTTPConnection) -> Any:
        return AuthCredentials(["authenticated"]), AuthenticatedUser(user)

    return f


@pytest.fixture()
def authuser(monkeypatch):
    """Fixture for an authenticated whose roles abnd permissions can be tweaked."""
    user = MockUser()
    monkeypatch.setattr(
        saltapi.auth.authorization.TokenAuthenticationBackend,
        "authenticate",
        mock_authenticate(user),
    )

    yield user
