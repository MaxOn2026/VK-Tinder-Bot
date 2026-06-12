from config import Config
import psycopg2



class DBManager:
    def __init__(self):
        self.conn_params = {
            'host': Config.HOST,
            'port': Config.PORT,
            'database': Config.DATABASE,
            'user': Config.USER,
            'password': Config.PASSWORD
        }

    def get_connection(self):
        return psycopg2.connect(kwargs=self.conn_params)

    def execute_query(self, query: str, params: list|None=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cur.fetchall()
                conn.commit()
                return cur.rowcount
            
        finally:
            conn.close()
            
    def execute_many(self, query: str, params: list|None=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.executemany(query, params)
                conn.commit()
                return cur.rowcount
        finally:
            conn.close()
            
    def create_tables