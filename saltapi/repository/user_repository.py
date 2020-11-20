"""Access user  details from the database."""

import dataclasses
from typing import List, Optional

from saltapi.repository.database import database


@dataclasses.dataclass(frozen=True)
class User:
    """A SALT user."""

    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    roles: List[str]
    permissions: List[str]


async def find_user_by_credentials(username: str, password: str) -> Optional[User]:
    """
    Find the user with a given username and password.

    In case the user credentials are invalid None is returned.

    Parameters
    ----------
    username : str
        The PIPT username.
    password : str
        The password of the user.

    Returns
    -------
    None.
    """
    query = """
SELECT PiptUser_Id
FROM PiptUser
WHERE Username=:username AND Password=MD5(:password)
    """
    values = {"username": username, "password": password}
    result = await database.fetch_one(query=query, values=values)
    if not result:
        return None
    return await find_user_by_id(result[0])


async def find_user_by_id(user_id: int) -> Optional[User]:
    """
    Find the user with a given user id.

    In case the user id does not exist None is returned.

    Parameters
    ----------
    user_id
        A PIPT user id.

    Returns
    -------
        The user.
    """
    sql = """
SELECT
    Username,
    FirstName,
    Surname,
    Email
FROM PiptUser AS u
    JOIN Investigator AS i using (Investigator_Id)
WHERE u.PiptUser_Id = :user_id
    """
    values = {"user_id": user_id}
    result = await database.fetch_one(query=sql, values=values)
    if not result:
        return None

    return User(
        id=user_id,
        username=result[0],
        first_name=result[1],
        last_name=result[2],
        email=result[3],
        roles=[],  # TODO: get user roles
        permissions=[],  # TODO: get user permissions
    )
