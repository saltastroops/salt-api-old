import jwt
import os

from starlette.responses import JSONResponse

from database.user_queries import query_id, verify_user
from util.error import InvalidUsage


def create_token(username):
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

    user_id = query_id(username)
    if user_id is None:
        raise Exception(f'User not found: {username}')
    user = {
        'user_id': f'{user_id}'
    }
    token = jwt.encode(user, os.environ['SECRET_TOKEN_KEY'], algorithm='HS256').decode('utf-8')

    return token


def get_user_token(credentials):
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


def login_user(request):
    print(request.json)
    token = "I am a token"
    return JSONResponse({
        "token": token,
        "isAuthenticated": "True",
        "user": {
            "username": "",
            "email": "",
            "role": "admin",
            "permissions": ["CAN SUBMIT PROPOSALS"]
        }
    })