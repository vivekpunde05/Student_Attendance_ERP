import mysql.connector
from mysql.connector import pooling
from config import DB_CONFIG

_pool = None

def init_pool(pool_size=5):
    global _pool
    if _pool is None:
        _pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="attendance_pool",
            pool_size=pool_size,
            **DB_CONFIG
        )

def get_conn():
    global _pool
    if _pool is None:
        init_pool()
    return _pool.get_connection()

def execute(query, params=None, fetch=False, many=False, commit=False):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        if many:
            cursor.executemany(query, params or [])
        else:
            cursor.execute(query, params or ())
        result = None
        if fetch:
            result = cursor.fetchall()
        if commit:
            conn.commit()
        return result
    finally:
        cursor.close()
        conn.close()
