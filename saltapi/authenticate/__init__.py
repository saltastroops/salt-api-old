"""Authentication and authorization."""
from typing import Dict

import jwt
import os

from starlette.responses import JSONResponse

from saltapi.repository.user_repository import find_user_id_by_credentials, find_user_by_id
from saltapi.util.error import InvalidUsage


def create_token(credentials: Dict[str, str]) -> str:
    if credentials is None:
        raise InvalidUsage(message='Username or password not provided', status_code=400)
    try:
        username = credentials['username']
        password = credentials['password']
    except KeyError:
        raise InvalidUsage(message='Username or password not provided', status_code=400)

    user_id = find_user_id_by_credentials(username, password)
    return jwt.encode({"user_id": f"{user_id}"}, os.environ['SECRET_TOKEN_KEY'], algorithm='HS256').decode('utf-8')


def is_valid_token(token):
    try:
        user = jwt.decode(token, os.environ['SECRET_TOKEN_KEY'], algorithm='HS256')

        if 'user_id' in user:
            return True
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
        "token": create_token(body["credentials"]),
    })
