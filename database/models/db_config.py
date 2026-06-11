import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'vkinder_db',
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD')
    }

def get_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def execute_query(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return cur.fetchall()
            conn.commit()
            return cur.rowcount
        
    finally:
        conn.close()