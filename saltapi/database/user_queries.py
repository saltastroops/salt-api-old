from typing import Optional, Dict

import pandas as pd

from saltapi.database.sdb_connection import sdb_connect
from saltapi.util.error import InvalidUsage


def query_user_id(username: str) -> Optional[int]:
    """
    Query the PIPT user id.

    Parameters
    ----------
    username : str
        The PIPT username.

    Returns
    -------
    user_is: int
        The PIPT user id.
    """
    sql = """SELECT PiptUser_Id
             FROM PiptUser
             WHERE Username='{username}'""" \
        .format(username=username)

    conn = sdb_connect()
    try:
        result = pd.read_sql(sql, conn)
        conn.close()
        return result.iloc[0]['PiptUser_Id']
    except IndexError:
        return None


def verify_user(username: str, password: str) -> Optional:
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
    sql = """SELECT COUNT(PiptUser_Id) AS UserCount
             FROM PiptUser
             WHERE Username='{username}' AND Password=MD5('{password}')""" \
        .format(username=username, password=password)

    conn = sdb_connect()
    result = pd.read_sql(sql, conn)
    conn.close()
    if not result.iloc[0]['UserCount']:
        raise InvalidUsage('Username or password wrong')

    return True


def query_user(user_id: int) -> Dict:
    """
    Query user details
    Parameters
    ----------
    user_id

    Returns
    -------

    """

    sql = '''
    SELECT * FROM PiptUser AS u
        JOIN Investigator AS i using (Investigator_Id)
    WHERE u.PiptUser_Id = {user_id}
    '''.format(user_id=user_id)
    conn = sdb_connect()
    results = pd.read_sql(sql, conn)
    conn.close()

    return {
        "username": results["Username"][0],
        "first_name": results["FirstName"][0],
        "last_name": results["Surname"][0],
        "email": results["Email"][0],
        "role": [] # Todo get user roles
    }
