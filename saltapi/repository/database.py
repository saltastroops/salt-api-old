import asyncio
from aiomysql import connect
import os


sql_config = {
    'user': os.environ["API_USER"],
    'host': os.environ["API_HOST"],
    'password': os.getenv("API_PASSWORD"),
    'db': os.getenv("API_DATABASE"),
    'charset': 'utf8'
}


async def sdb_connect() -> connect:
    return await connect(**sql_config)
