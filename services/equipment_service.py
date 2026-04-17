import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import get_db

class EquipmentService:
    """器材服务"""

    def get_all_equipment(self):
        """获取所有器材"""
        sql = "SELECT * FROM equipment ORDER BY id"
        return get_db().execute_query(sql)

    def get_available_equipment(self):
        """获取在库器材"""
        sql = "SELECT * FROM equipment WHERE status = '在库' ORDER BY id"
        return get_db().execute_query(sql)

    def get_equipment_by_id(self, equipment_id):
        """根据ID获取器材"""
        sql = "SELECT * FROM equipment WHERE id = %s"
        result = get_db().execute_query(sql, (equipment_id,))
        return result[0] if result else None

    def add_equipment(self, name, equipment_type, buy_date=None, remark=None):
        """添加器材"""
        sql = "INSERT INTO equipment (name, equipment_type, status, buy_date, remark) VALUES (%s, %s, '在库', %s, %s)"
        return get_db().execute_update(sql, (name, equipment_type, buy_date, remark))

    def update_equipment(self, equipment_id, name, equipment_type, remark):
        """更新器材"""
        sql = "UPDATE equipment SET name=%s, equipment_type=%s, remark=%s WHERE id=%s"
        return get_db().execute_update(sql, (name, equipment_type, remark, equipment_id))

    def delete_equipment(self, equipment_id):
        """删除器材"""
        sql = "DELETE FROM equipment WHERE id = %s"
        return get_db().execute_update(sql, (equipment_id,))


class EquipmentBorrowService:
    """器材借用服务"""

    def get_all_borrow_records(self):
        """获取所有借用记录"""
        sql = """SELECT eb.*, e.name AS equipment_name, e.equipment_type,
                        m.name AS member_name, m.phone AS member_phone
                 FROM equipment_borrow eb
                 JOIN equipment e ON eb.equipment_id = e.id
                 JOIN member m ON eb.member_id = m.id
                 ORDER BY eb.borrow_time DESC"""
        return get_db().execute_query(sql)

    def get_borrow_record_by_id(self, record_id):
        """根据ID获取借用记录"""
        sql = """SELECT eb.*, e.name AS equipment_name, m.name AS member_name
                 FROM equipment_borrow eb
                 JOIN equipment e ON eb.equipment_id = e.id
                 JOIN member m ON eb.member_id = m.id
                 WHERE eb.id = %s"""
        result = get_db().execute_query(sql, (record_id,))
        return result[0] if result else None

    def borrow_equipment(self, equipment_id, member_id):
        """借用器材"""
        # 检查器材是否在库
        equipment = EquipmentService().get_equipment_by_id(equipment_id)
        if not equipment:
            raise ValueError("器材不存在")
        if equipment['status'] != '在库':
            raise ValueError("器材不在库中，无法借用")

        # 创建借用记录
        sql = "INSERT INTO equipment_borrow (equipment_id, member_id) VALUES (%s, %s)"
        get_db().execute_update(sql, (equipment_id, member_id))

        # 更新器材状态
        update_sql = "UPDATE equipment SET status = '借出' WHERE id = %s"
        get_db().execute_update(update_sql, (equipment_id,))

        return True

    def return_equipment(self, record_id):
        """归还器材"""
        record = self.get_borrow_record_by_id(record_id)
        if not record:
            raise ValueError("借用记录不存在")
        if record['status'] == '已归还':
            raise ValueError("器材已归还")

        # 更新借用记录
        sql = "UPDATE equipment_borrow SET return_time = NOW(), status = '已归还' WHERE id = %s"
        get_db().execute_update(sql, (record_id,))

        # 更新器材状态
        update_sql = "UPDATE equipment SET status = '在库' WHERE id = %s"
        get_db().execute_update(update_sql, (record['equipment_id'],))

        return True

    def get_member_borrow_records(self, member_id):
        """获取指定会员的借用记录"""
        sql = """SELECT eb.*, e.name AS equipment_name, e.equipment_type
                 FROM equipment_borrow eb
                 JOIN equipment e ON eb.equipment_id = e.id
                 WHERE eb.member_id = %s
                 ORDER BY eb.borrow_time DESC"""
        return get_db().execute_query(sql, (member_id,))

    def get_current_borrow_records(self):
        """获取当前借出中的记录"""
        sql = """SELECT eb.*, e.name AS equipment_name, e.equipment_type,
                        m.name AS member_name, m.phone AS member_phone
                 FROM equipment_borrow eb
                 JOIN equipment e ON eb.equipment_id = e.id
                 JOIN member m ON eb.member_id = m.id
                 WHERE eb.status = '借用中'
                 ORDER BY eb.borrow_time DESC"""
        return get_db().execute_query(sql)
