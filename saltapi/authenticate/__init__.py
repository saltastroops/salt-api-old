"""Authentication and authorization."""
from typing import Dict

import jwt
import os

from starlette.responses import JSONResponse

from saltapi.repository.user_repository import find_user_id_by_credentials
from saltapi.util.error import InvalidUsage


async def create_token(credentials: Dict[str, str]) -> str:
    if credentials is None:
        raise InvalidUsage(message='Username or password not provided', status_code=400)
    try:
        username = credentials['username']
        password = credentials['password']
    except KeyError:
        raise InvalidUsage(message='Username or password not provided', status_code=400)

    user_id = await find_user_id_by_credentials(username, password)
    return jwt.encode({"user_id": f"{user_id}"}, os.environ['SECRET_TOKEN_KEY'], algorithm='HS256').decode('utf-8')


def validate_token(token):
    """
    Validate the user token. If the token can not be decoded then raise and error
    Parameters
    ----------
    token

    Returns
    -------

    """
    try:
        user_id = jwt.decode(token, os.environ['SECRET_TOKEN_KEY'], algorithm='HS256')

        if 'user_id' in user_id:
            return
        raise ValueError("The user token have been modifies.")
    except Exception as e:
        raise ValueError("Invalid user token.")


def get_user_id_from_token(token):
    """
    Get the user id from the token.

    Parameters
    ----------
    token

    Returns
    -------

    """
    try:
        user_id = jwt.decode(token, os.environ['SECRET_TOKEN_KEY'], algorithm='HS256')

        if 'user_id' in user_id:
            return user_id["user_id"]
        return False
    except Exception as e:
        return False


async def login_user(request) -> JSONResponse:
    """

    Parameters
    ----------
    request
        Http request

    Returns
    -------
    User token
    """
    body = await request.json()
    return JSONResponse({
        "token": await create_token(body["credentials"]),
    })
