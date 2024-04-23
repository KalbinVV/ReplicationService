import sqlite3
from typing import Optional


class ContextCursor:
    def __init__(self, connection: sqlite3.Connection):
        self.__connection = connection
        self.__cursor: Optional[sqlite3.Cursor] = None

    def __enter__(self):
        self.__cursor = self.__connection.cursor()

        return self.__cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__cursor.close()
