import sqlite3
import os

def run_sql(sql, params=()):
    conn = sqlite3.connect(os.environ["DB_PATH"])
    cursor = conn.cursor()
    try:
        # cursor.execute(sql)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
    except Exception as e:
        conn.close()
        raise ValueError(f"Error executing SQL: {e}")

    conn.close()
    return rows