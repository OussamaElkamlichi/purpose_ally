import mysql.connector
import os

class dbConnet:
    _conn = None
    _cursor = None

    @classmethod
    def connect(cls):
        if cls._conn is None:  # Only create a new connection if it doesn't exist
            config = {
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD'),
                'host': os.getenv('DB_HOST'),
                'database': os.getenv('DB_DATABASE'),
            }
            cls._conn = mysql.connector.connect(**config)
            cls._cursor = cls._conn.cursor()

        return cls._cursor, cls._conn

    @classmethod
    def close(cls):
        if cls._conn:
            cls._cursor.close()
            cls._conn.close()
            cls._conn = None
            cls._cursor = None
