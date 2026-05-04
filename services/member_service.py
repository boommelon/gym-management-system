import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import get_db

class MemberService:
    """会员服务"""

    def get_all_members(self):
        """获取所有会员"""
        sql = "SELECT * FROM member ORDER BY id"
        return get_db().execute_query(sql)

    def search_member(self, keyword):
        """搜索会员"""
        sql = "SELECT * FROM member WHERE name LIKE %s OR phone LIKE %s ORDER BY id"
        params = (f"%{keyword}%", f"%{keyword}%")
        return get_db().execute_query(sql, params)

    def get_member_by_id(self, member_id):
        """根据ID获取会员"""
        sql = "SELECT * FROM member WHERE id = %s"
        result = get_db().execute_query(sql, (member_id,))
        return result[0] if result else None

    def add_member(self, name, phone, gender, id_card=None, remark=None):
        """添加会员"""
        sql = "INSERT INTO member (name, phone, gender, id_card, remark) VALUES (%s, %s, %s, %s, %s)"
        return get_db().execute_update(sql, (name, phone, gender, id_card, remark))

    def update_member(self, member_id, name, phone, gender, id_card, remark, status):
        """更新会员信息"""
        sql = """UPDATE member SET name=%s, phone=%s, gender=%s, id_card=%s, remark=%s, status=%s
                 WHERE id=%s"""
        return get_db().execute_update(sql, (name, phone, gender, id_card, remark, status, member_id))

    def delete_member(self, member_id):
        """删除会员"""
        sql = "DELETE FROM member WHERE id = %s"
        return get_db().execute_update(sql, (member_id,))


class CardTypeService:
    """卡类型服务"""

    def get_all_card_types(self):
        """获取所有卡类型"""
        sql = "SELECT * FROM card_type ORDER BY id"
        return get_db().execute_query(sql)

    def get_card_type_by_id(self, card_type_id):
        """根据ID获取卡类型"""
        sql = "SELECT * FROM card_type WHERE id = %s"
        result = get_db().execute_query(sql, (card_type_id,))
        return result[0] if result else None

    def add_card_type(self, name, card_category, times_limit, valid_days, price, description):
        """添加卡类型"""
        sql = """INSERT INTO card_type (name, card_category, times_limit, valid_days, price, description)
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        return get_db().execute_update(sql, (name, card_category, times_limit, valid_days, price, description))

    def update_card_type(self, card_type_id, name, card_category, times_limit, valid_days, price, description):
        """更新卡类型"""
        sql = """UPDATE card_type SET name=%s, card_category=%s, times_limit=%s, valid_days=%s, price=%s, description=%s
                 WHERE id=%s"""
        return get_db().execute_update(sql, (name, card_category, times_limit, valid_days, price, description, card_type_id))

    def get_card_type_options(self):
        """获取基础卡类型选项。"""
        return [
            {"label": "次卡", "requires_times_limit": True, "requires_valid_days": False},
            {"label": "月卡", "requires_times_limit": False, "requires_valid_days": True},
            {"label": "季卡", "requires_times_limit": False, "requires_valid_days": True},
            {"label": "年卡", "requires_times_limit": False, "requires_valid_days": True},
        ]


class MemberCardService:
    """会员卡服务"""

    def get_all_member_cards(self):
        """获取所有会员卡"""
        sql = """SELECT mc.*, m.name AS member_name, m.phone AS member_phone,
                        ct.name AS card_type_name, ct.card_category
                 FROM member_card mc
                 JOIN member m ON mc.member_id = m.id
                 JOIN card_type ct ON mc.card_type_id = ct.id
                 ORDER BY mc.id DESC"""
        return get_db().execute_query(sql)

    def get_member_cards(self, member_id):
        """获取指定会员的会员卡"""
        sql = """SELECT mc.*, ct.name AS card_type_name, ct.card_category
                 FROM member_card mc
                 JOIN card_type ct ON mc.card_type_id = ct.id
                 WHERE mc.member_id = %s
                 ORDER BY mc.buy_date DESC"""
        return get_db().execute_query(sql, (member_id,))

    def get_valid_member_card(self, member_id):
        """获取会员的有效会员卡"""
        sql = """SELECT mc.*, ct.name AS card_type_name, ct.card_category
                 FROM member_card mc
                 JOIN card_type ct ON mc.card_type_id = ct.id
                 WHERE mc.member_id = %s AND mc.status = '正常'
                   AND (mc.expire_date IS NULL OR mc.expire_date >= CURDATE())
                   AND (mc.remain_times IS NULL OR mc.remain_times > 0)
                 ORDER BY mc.buy_date DESC LIMIT 1"""
        result = get_db().execute_query(sql, (member_id,))
        return result[0] if result else None

    def add_member_card(self, member_id, card_type_id, price, buy_date=None):
        """办理会员卡"""
        # 获取卡类型信息
        card_type = CardTypeService().get_card_type_by_id(card_type_id)
        if not card_type:
            raise ValueError("卡类型不存在")

        from datetime import datetime, timedelta

        # 计算有效期
        expire_date = None
        remain_times = None

        if card_type['card_category'] == '次卡':
            remain_times = card_type['times_limit']
        else:
            if buy_date:
                buy_dt = datetime.strptime(buy_date, '%Y-%m-%d') if isinstance(buy_date, str) else buy_date
            else:
                buy_dt = datetime.now()
            expire_date = (buy_dt + timedelta(days=card_type['valid_days'])).strftime('%Y-%m-%d')

        sql = """INSERT INTO member_card (member_id, card_type_id, buy_date, expire_date, remain_times, status, price)
                 VALUES (%s, %s, %s, %s, %s, '正常', %s)"""

        if buy_date is None:
            buy_date = datetime.now().strftime('%Y-%m-%d')

        return get_db().execute_update(sql, (member_id, card_type_id, buy_date, expire_date, remain_times, price))

    def get_member_card_summary(self, member_id):
        """获取会员当前有效会员卡摘要。"""
        valid_card = self.get_valid_member_card(member_id)
        if valid_card:
            if valid_card["card_category"] == "次卡":
                summary = f"{valid_card['card_type_name']}，剩余 {valid_card.get('remain_times', 0)} 次"
            else:
                summary = f"{valid_card['card_type_name']}，有效期至 {valid_card.get('expire_date')}"
            return {"has_valid_card": True, "summary": summary, "card": valid_card}

        return {"has_valid_card": False, "summary": "暂无有效会员卡", "card": None}

    def get_member_consumption(self, member_id):
        """获取会员消费明细（调用存储过程）"""
        result = get_db().call_procedure('sp_member_detail', (member_id,))
        return result
