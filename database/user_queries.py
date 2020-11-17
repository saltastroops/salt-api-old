import pandas as pd

from database.sdb_connection import sdb_connect
from util.error import InvalidUsage


def query_id(username):
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


def verify_user(username, password):
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