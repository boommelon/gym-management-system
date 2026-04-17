import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import get_db

class CoachService:
    """教练服务"""

    def get_all_coaches(self):
        """获取所有教练"""
        sql = "SELECT * FROM coach WHERE status = '在职' ORDER BY id"
        return get_db().execute_query(sql)

    def get_coach_by_id(self, coach_id):
        """根据ID获取教练"""
        sql = "SELECT * FROM coach WHERE id = %s"
        result = get_db().execute_query(sql, (coach_id,))
        return result[0] if result else None

    def search_coach(self, keyword):
        """搜索教练"""
        sql = "SELECT * FROM coach WHERE (name LIKE %s OR phone LIKE %s) AND status = '在职' ORDER BY id"
        params = (f"%{keyword}%", f"%{keyword}%")
        return get_db().execute_query(sql, params)

    def add_coach(self, name, phone, gender, specialty, salary):
        """添加教练"""
        sql = "INSERT INTO coach (name, phone, gender, specialty, salary) VALUES (%s, %s, %s, %s, %s)"
        return get_db().execute_update(sql, (name, phone, gender, specialty, salary))

    def update_coach(self, coach_id, name, phone, gender, specialty, salary):
        """更新教练信息"""
        sql = """UPDATE coach SET name=%s, phone=%s, gender=%s, specialty=%s, salary=%s
                 WHERE id=%s"""
        return get_db().execute_update(sql, (name, phone, gender, specialty, salary, coach_id))

    def delete_coach(self, coach_id):
        """删除教练（离职）"""
        sql = "UPDATE coach SET status = '离职' WHERE id = %s"
        return get_db().execute_update(sql, (coach_id,))


class CourseService:
    """课程服务"""

    def get_all_courses(self):
        """获取所有课程"""
        sql = "SELECT * FROM course ORDER BY id"
        return get_db().execute_query(sql)

    def get_course_by_id(self, course_id):
        """根据ID获取课程"""
        sql = "SELECT * FROM course WHERE id = %s"
        result = get_db().execute_query(sql, (course_id,))
        return result[0] if result else None

    def add_course(self, name, category, duration, max_capacity, description):
        """添加课程"""
        sql = """INSERT INTO course (name, category, duration, max_capacity, description)
                 VALUES (%s, %s, %s, %s, %s)"""
        return get_db().execute_update(sql, (name, category, duration, max_capacity, description))

    def update_course(self, course_id, name, category, duration, max_capacity, description):
        """更新课程"""
        sql = """UPDATE course SET name=%s, category=%s, duration=%s, max_capacity=%s, description=%s
                 WHERE id=%s"""
        return get_db().execute_update(sql, (name, category, duration, max_capacity, description, course_id))

    def delete_course(self, course_id):
        """删除课程"""
        sql = "DELETE FROM course WHERE id = %s"
        return get_db().execute_update(sql, (course_id,))


class CourseScheduleService:
    """课程安排服务"""

    def get_all_schedules(self):
        """获取所有课程安排"""
        sql = """SELECT cs.*, c.name AS course_name, c.category AS course_category,
                        co.name AS coach_name
                 FROM course_schedule cs
                 JOIN course c ON cs.course_id = c.id
                 JOIN coach co ON cs.coach_id = co.id
                 ORDER BY cs.schedule_time DESC"""
        return get_db().execute_query(sql)

    def get_upcoming_schedules(self, days=7):
        """获取未来几天的课程安排"""
        sql = """SELECT cs.*, c.name AS course_name, c.category AS course_category,
                        co.name AS coach_name
                 FROM course_schedule cs
                 JOIN course c ON cs.course_id = c.id
                 JOIN coach co ON cs.coach_id = co.id
                 WHERE cs.schedule_time >= NOW() AND cs.schedule_time <= DATE_ADD(NOW(), INTERVAL %s DAY)
                 ORDER BY cs.schedule_time"""
        return get_db().execute_query(sql, (days,))

    def get_schedule_by_id(self, schedule_id):
        """根据ID获取课程安排"""
        sql = """SELECT cs.*, c.name AS course_name, c.category AS course_category,
                        co.name AS coach_name
                 FROM course_schedule cs
                 JOIN course c ON cs.course_id = c.id
                 JOIN coach co ON cs.coach_id = co.id
                 WHERE cs.id = %s"""
        result = get_db().execute_query(sql, (schedule_id,))
        return result[0] if result else None

    def add_schedule(self, course_id, coach_id, schedule_time, room, max_capacity):
        """添加课程安排"""
        sql = """INSERT INTO course_schedule (course_id, coach_id, schedule_time, room, max_capacity, status)
                 VALUES (%s, %s, %s, %s, %s, '未开始')"""
        return get_db().execute_update(sql, (course_id, coach_id, schedule_time, room, max_capacity))

    def update_schedule(self, schedule_id, course_id, coach_id, schedule_time, room, max_capacity):
        """更新课程安排"""
        sql = """UPDATE course_schedule SET course_id=%s, coach_id=%s, schedule_time=%s,
                 room=%s, max_capacity=%s WHERE id=%s"""
        return get_db().execute_update(sql, (course_id, coach_id, schedule_time, room, max_capacity, schedule_id))

    def delete_schedule(self, schedule_id):
        """删除课程安排"""
        sql = "DELETE FROM course_schedule WHERE id = %s"
        return get_db().execute_update(sql, (schedule_id,))


class BookingService:
    """预约签到服务"""

    def get_all_bookings(self):
        """获取所有预约记录"""
        sql = """SELECT b.*, m.name AS member_name, m.phone AS member_phone,
                        c.name AS course_name, cs.schedule_time
                 FROM booking b
                 JOIN member m ON b.member_id = m.id
                 JOIN course_schedule cs ON b.schedule_id = cs.id
                 JOIN course c ON cs.course_id = c.id
                 ORDER BY b.book_time DESC"""
        return get_db().execute_query(sql)

    def get_member_bookings(self, member_id):
        """获取指定会员的预约记录"""
        sql = """SELECT b.*, c.name AS course_name, cs.schedule_time, co.name AS coach_name
                 FROM booking b
                 JOIN course_schedule cs ON b.schedule_id = cs.id
                 JOIN course c ON cs.course_id = c.id
                 JOIN coach co ON cs.coach_id = co.id
                 WHERE b.member_id = %s
                 ORDER BY cs.schedule_time DESC"""
        return get_db().execute_query(sql, (member_id,))

    def get_schedule_bookings(self, schedule_id):
        """获取指定课程安排的预约会员"""
        sql = """SELECT b.*, m.name AS member_name, m.phone AS member_phone
                 FROM booking b
                 JOIN member m ON b.member_id = m.id
                 WHERE b.schedule_id = %s
                 ORDER BY b.book_time"""
        return get_db().execute_query(sql, (schedule_id,))

    def book_course(self, member_id, schedule_id):
        """会员预约课程"""
        # 检查是否已有预约
        sql = "SELECT id FROM booking WHERE member_id = %s AND schedule_id = %s"
        existing = get_db().execute_query(sql, (member_id, schedule_id))
        if existing:
            raise ValueError("该课程已预约")

        # 检查课程是否还有名额
        schedule = CourseScheduleService().get_schedule_by_id(schedule_id)
        if not schedule:
            raise ValueError("课程不存在")
        if schedule['current_count'] >= schedule['max_capacity']:
            raise ValueError("课程名额已满")

        # 创建预约
        sql = "INSERT INTO booking (member_id, schedule_id) VALUES (%s, %s)"
        get_db().execute_update(sql, (member_id, schedule_id))

        # 更新课程预约人数
        update_sql = """UPDATE course_schedule SET current_count = current_count + 1
                       WHERE id = %s"""
        get_db().execute_update(update_sql, (schedule_id,))

        return True

    def checkin_booking(self, booking_id):
        """会员签到"""
        sql = "UPDATE booking SET checkin_time = NOW(), status = '已签到' WHERE id = %s AND checkin_time IS NULL"
        affected = get_db().execute_update(sql, (booking_id,))
        if affected == 0:
            raise ValueError("签到失败，可能已签到或预约不存在")
        return True

    def cancel_booking(self, booking_id):
        """取消预约"""
        # 获取预约信息
        sql = "SELECT schedule_id FROM booking WHERE id = %s"
        result = get_db().execute_query(sql, (booking_id,))
        if not result:
            raise ValueError("预约不存在")

        schedule_id = result[0]['schedule_id']

        # 更新预约状态
        sql = "UPDATE booking SET status = '已取消' WHERE id = %s"
        get_db().execute_update(sql, (booking_id,))

        # 减少课程预约人数
        update_sql = "UPDATE course_schedule SET current_count = current_count - 1 WHERE id = %s"
        get_db().execute_update(update_sql, (schedule_id,))

        return True

    def rate_booking(self, booking_id, rating, remark):
        """评价课程"""
        sql = "UPDATE booking SET rating = %s, remark = %s WHERE id = %s"
        return get_db().execute_update(sql, (rating, remark, booking_id))


class WeeklyStatsService:
    """课程统计服务"""

    def get_weekly_stats(self):
        """获取近一周课程统计（调用视图）"""
        sql = "SELECT * FROM v_course_weekly_stats ORDER BY booking_count DESC"
        return get_db().execute_query(sql)
