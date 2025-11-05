import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

# DB 커넥션 풀
dbconfig = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="ai_pool",
    pool_size=5,
    **dbconfig
)

def get_connection():
    try:
        conn = connection_pool.get_connection()
        return conn
    except mysql.connector.Error as e:
        logging.error(f"DB 연결 실패: {e}")
        return None
