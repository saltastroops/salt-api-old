from typing import Optional, Dict

from saltapi.repository.database import sdb_connection
from saltapi.util.error import InvalidUsage


async def find_user_id_by_credentials(username: str, password: str) -> Optional:
    """
    Verify the username and password of the user.

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
    sql = f"""
SELECT PiptUser_Id
FROM PiptUser
WHERE Username='{username}' AND Password=MD5('{password}')
    """

    result = await sdb_connection.fetch_all(query=sql)
    if not len(result):
        raise InvalidUsage('Username or password wrong')

    return result[0][0]


async def find_user_by_id(user_id: int) -> Dict:
    """
    Query user details by user id.

    Parameters
    ----------
    user_id
        A PIPT user id
    Returns
    -------
        The user Details

    """

    sql = f'''
SELECT 
    Username,
    FirstName,
    Surname,
    Email 
FROM PiptUser AS u
    JOIN Investigator AS i using (Investigator_Id)
WHERE u.PiptUser_Id = {user_id}
    '''
    results = await sdb_connection.fetch_all(query=sql)
    if not len(results):
        raise InvalidUsage(message="User id is not recognised", status_code=500)

    return {
        "username": results[0][0],
        "first_name": results[0][1],
        "last_name": results[0][2],
        "email": results[0][3],
        "role": [] # Todo get user roles
    }

