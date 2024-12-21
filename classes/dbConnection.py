import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables only once

class dbConnect:
    _conn = None
    _cursor = None

    @classmethod
    def connect(cls):
        if cls._conn is None:
            config = {
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD'),
                'host': os.getenv('DB_HOST'),
                'database': os.getenv('DB_DATABASE'),
            }
            try:
                cls._conn = mysql.connector.connect(**config)
                cls._cursor = cls._conn.cursor()
                print("Database connected.") # only prints when first connected
            except mysql.connector.Error as err:
                print(f"Database connection error: {err}")
                return None, None
        return cls._cursor, cls._conn

    @classmethod
    def close(cls):
        if cls._conn:
            cls._cursor.close()
            cls._conn.close()
            cls._conn = None
            cls._cursor = None
            print("Database connection closed.")