"""Testing authentication."""
import json
from typing import Optional

import pytest
from starlette.testclient import TestClient

from saltapi.app import app
from saltapi.repository import user_repository
from saltapi.repository.user_repository import User

USER_ID = 42


async def mock_find_user_by_credentials(username: str, password: str) -> Optional[User]:
    """Mock finding a user by credentials."""
    if username == "jane" and password == "secret":
        return User(
            id=USER_ID,
            username="jane",
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            roles=[],
            permissions=[],
        )
    else:
        return None


async def mock_find_user_by_id(user_id: int) -> Optional[User]:
    """Mock finding a user by id."""
    if user_id == USER_ID:
        return User(
            id=USER_ID,
            username="jane",
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            roles=[],
            permissions=[],
        )
    else:
        return None


def test_cannot_authenticate_with_missing_username():
    """
    Test an attempt to authenticate without a username.

    Trying to request an authentication token without a username results in a
    Bad Request error.
    """
    data = {"password": "secret"}
    client = TestClient(app)
    response = client.post("/token", data=json.dumps(data))
    assert response.status_code == 400


def test_cannot_authenticate_with_missing_password():
    """
    Test an attempt to authenticate without a password.

    Trying to request an authentication token without a password results in a
    Bad Request error.
    """
    data = {"username": "jane"}
    client = TestClient(app)
    response = client.post("/token", data=json.dumps(data))
    assert response.status_code == 400


def test_cannot_authenticate_with_invalid_credentials(monkeypatch):
    """
    Test an attempt to authenticate with invalid credentials.

    Trying to request an authentication token with invalid credentials results in a
    Not Authorized error.
    """
    monkeypatch.setattr(
        user_repository, "find_user_by_credentials", mock_find_user_by_credentials
    )
    client = TestClient(app)
    data = {"username": "jane", "password": "incorrect"}
    response = client.post("/token", data=json.dumps(data))
    assert response.status_code == 401


@pytest.mark.parametrize("header_value", [("abcd"), ("Bearer abcd")])
def test_cannot_authenticate_with_invalid_token(header_value):
    """
    Test an attempt to authenticate with an invalid token.

    Trying to authenticate with an invalid authentication token results in a
    Bad Request error.
    """
    client = TestClient(app)
    response = client.get("/graphql", headers={"Authorization": "Bearer abcd"})
    assert response.status_code == 400


def test_can_authenticate_with_valid_token(monkeypatch):
    """Request a token and then authenticate with it."""
    monkeypatch.setattr(
        user_repository, "find_user_by_credentials", mock_find_user_by_credentials
    )
    monkeypatch.setattr(user_repository, "find_user_by_id", mock_find_user_by_id)

    # request a token
    client = TestClient(app)
    data = {"username": "jane", "password": "secret"}
    response = client.post("/token", json.dumps(data))
    assert response.status_code == 200
    payload = response.json()
    assert "token" in payload
    token = payload["token"]

    # authenticate with this token
    r = client.get("/graphql", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
