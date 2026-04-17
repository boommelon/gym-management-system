import configparser
import pymysql
import os

class DatabaseConfig:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'config.ini')

        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')

        self.host = self.config.get('database', 'host')
        self.port = self.config.getint('database', 'port')
        self.user = self.config.get('database', 'user')
        self.password = self.config.get('database', 'password')
        self.database = self.config.get('database', 'database')
        self.charset = self.config.get('database', 'charset')


class DatabaseConnection:
    def __init__(self, config_path=None):
        self.config = DatabaseConfig(config_path)
        self.connection = None

    def connect(self):
        if self.connection is None or not self.connection.open:
            try:
                self.connection = pymysql.connect(
                    host=self.config.host,
                    port=self.config.port,
                    user=self.config.user,
                    password=self.config.password,
                    database=self.config.database,
                    charset=self.config.charset,
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=False
                )
            except pymysql.Error as e:
                print(f"Database connection failed: {e}")
                raise
        return self.connection

    def close(self):
        if self.connection and self.connection.open:
            self.connection.close()
            self.connection = None

    def execute_query(self, sql, params=None):
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            self.close()

    def execute_update(self, sql, params=None):
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                affected = cursor.execute(sql, params)
                conn.commit()
                return affected
        except Exception as e:
            conn.rollback()
            raise
        finally:
            self.close()

    def call_procedure(self, proc_name, args=None):
        conn = self.connect()
        try:
            cursor = conn.cursor()
            try:
                if args:
                    cursor.callproc(proc_name, args)
                else:
                    cursor.callproc(proc_name)
                
                results = []
                while True:
                    result = cursor.fetchall()
                    if result:
                        results.extend(result)
                    if not cursor.nextset():
                        break
                return results
            finally:
                cursor.close()
        finally:
            self.close()


_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection()
    return _db_instance
