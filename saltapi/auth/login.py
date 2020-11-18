from typing import Dict

import jwt
import os

from starlette.responses import JSONResponse

from saltapi.database.user_queries import query_user_id, verify_user, query_user
from saltapi.util.error import InvalidUsage


def create_token(username: str) -> str:
    """
    Create a token containing the user id of the given PIPT user.

    Parameters
    ----------
    username : str
        The PIPT username.

    Returns
    -------
    The user token
    """
    user_id = query_user_id(username)
    if user_id is None:
        raise Exception(f'User not found: {username}')
    user = {
        'user_id': f'{user_id}'
    }
    token = jwt.encode(user, os.environ['SECRET_TOKEN_KEY'], algorithm='HS256').decode('utf-8')

    return token


def get_user_token(credentials: Dict[str, str]) -> str:
    if credentials is None:
        raise InvalidUsage(message='Username or password not provided', status_code=400)
    try:
        username = credentials['username']
        password = credentials['password']
    except KeyError:
        raise InvalidUsage(message='Username or password not provided', status_code=400)

    verify_user(username, password)
    return create_token(username)


def is_valid_token(token):
    try:
        user = jwt.decode(token, os.environ['SECRET_TOKEN_KEY'], algorithm='HS256')

        if 'user_id' in user:
            return True
        return False
    except Exception as e:
        return False


def login_user(request) -> JSONResponse:
    """

    Parameters
    ----------
    request
        Http request with user credentials

    Returns
    -------
    User token
    If user is authenticated.
    User details

    """

    username = ""
    password = ""

    if verify_user(username, password):
        return JSONResponse({
            "token": create_token(username),
            "isAuthenticated": "true",
            "user": query_user(query_user_id(username))
        })
    return JSONResponse({
        "isAuthenticated": "false",
        "message": "User can nor be authenticated username or password might be wrong."
    })