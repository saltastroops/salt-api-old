import databases as databases
import os

SDB_URL = os.environ["SDB_DSN"]

sdb_connection = databases.Database(SDB_URL)
