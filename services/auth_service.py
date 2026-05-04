import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import get_db


class AuthService:
    """管理员认证服务。"""

    def validate_admin(self, username, password):
        sql = """
            SELECT id, username, name
            FROM admin
            WHERE username = %s AND password = %s
            LIMIT 1
        """
        result = get_db().execute_query(sql, (username, password))
        return result[0] if result else None
