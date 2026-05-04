import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import get_db


class EquipmentService:
    """器材服务。"""

    def get_all_equipment(self):
        sql = "SELECT * FROM equipment ORDER BY id"
        return get_db().execute_query(sql)

    def get_available_equipment(self):
        sql = "SELECT * FROM equipment WHERE status = '在库' ORDER BY id"
        return get_db().execute_query(sql)

    def get_equipment_by_id(self, equipment_id):
        sql = "SELECT * FROM equipment WHERE id = %s"
        result = get_db().execute_query(sql, (equipment_id,))
        return result[0] if result else None

    def add_equipment(self, name, equipment_type, buy_date=None, remark=None):
        sql = """INSERT INTO equipment (name, equipment_type, status, buy_date, remark)
                 VALUES (%s, %s, '在库', %s, %s)"""
        return get_db().execute_update(sql, (name, equipment_type, buy_date, remark))

    def update_equipment(self, equipment_id, name, equipment_type, remark):
        sql = """UPDATE equipment
                 SET name = %s, equipment_type = %s, remark = %s
                 WHERE id = %s"""
        return get_db().execute_update(sql, (name, equipment_type, remark, equipment_id))

    def delete_equipment(self, equipment_id):
        sql = "DELETE FROM equipment WHERE id = %s"
        return get_db().execute_update(sql, (equipment_id,))


class EquipmentBorrowService:
    """器材借用服务。"""

    def get_all_borrow_records(self):
        sql = """SELECT eb.*, e.name AS equipment_name, e.equipment_type,
                        m.name AS member_name, m.phone AS member_phone
                 FROM equipment_borrow eb
                 JOIN equipment e ON eb.equipment_id = e.id
                 JOIN member m ON eb.member_id = m.id
                 ORDER BY eb.borrow_time DESC"""
        return get_db().execute_query(sql)

    def get_borrow_record_by_id(self, record_id):
        sql = """SELECT eb.*, e.name AS equipment_name, e.equipment_type, m.name AS member_name
                 FROM equipment_borrow eb
                 JOIN equipment e ON eb.equipment_id = e.id
                 JOIN member m ON eb.member_id = m.id
                 WHERE eb.id = %s"""
        result = get_db().execute_query(sql, (record_id,))
        return result[0] if result else None

    def borrow_equipment(self, equipment_id, member_id):
        db = get_db()
        with db.transaction() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, status FROM equipment WHERE id = %s FOR UPDATE",
                    (equipment_id,),
                )
                equipment = cursor.fetchone()
                if not equipment:
                    raise ValueError("器材不存在")
                if equipment["status"] != "在库":
                    raise ValueError("该器材当前不可借用")

                cursor.execute(
                    """INSERT INTO equipment_borrow (equipment_id, member_id, status)
                       VALUES (%s, %s, '借用中')""",
                    (equipment_id, member_id),
                )
                cursor.execute("UPDATE equipment SET status = '借出' WHERE id = %s", (equipment_id,))
        return True

    def return_equipment(self, record_id):
        db = get_db()
        with db.transaction() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, equipment_id, status FROM equipment_borrow WHERE id = %s FOR UPDATE",
                    (record_id,),
                )
                record = cursor.fetchone()
                if not record:
                    raise ValueError("借用记录不存在")
                if record["status"] != "借用中":
                    raise ValueError("该记录已经归还")

                cursor.execute(
                    "UPDATE equipment_borrow SET return_time = NOW(), status = '已归还' WHERE id = %s",
                    (record_id,),
                )
                cursor.execute("UPDATE equipment SET status = '在库' WHERE id = %s", (record["equipment_id"],))
        return True

    def get_member_borrow_records(self, member_id):
        sql = """SELECT eb.*, e.name AS equipment_name, e.equipment_type
                 FROM equipment_borrow eb
                 JOIN equipment e ON eb.equipment_id = e.id
                 WHERE eb.member_id = %s
                 ORDER BY eb.borrow_time DESC"""
        return get_db().execute_query(sql, (member_id,))

    def get_current_borrow_records(self):
        sql = """SELECT eb.*, e.name AS equipment_name, e.equipment_type,
                        m.name AS member_name, m.phone AS member_phone
                 FROM equipment_borrow eb
                 JOIN equipment e ON eb.equipment_id = e.id
                 JOIN member m ON eb.member_id = m.id
                 WHERE eb.status = '借用中'
                 ORDER BY eb.borrow_time DESC"""
        return get_db().execute_query(sql)
