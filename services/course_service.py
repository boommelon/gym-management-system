import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import get_db


class CoachService:
    """教练服务。"""

    def get_all_coaches(self):
        sql = "SELECT * FROM coach WHERE status = '在职' ORDER BY id"
        return get_db().execute_query(sql)

    def get_coach_by_id(self, coach_id):
        sql = "SELECT * FROM coach WHERE id = %s"
        result = get_db().execute_query(sql, (coach_id,))
        return result[0] if result else None

    def search_coach(self, keyword):
        sql = "SELECT * FROM coach WHERE (name LIKE %s OR phone LIKE %s) AND status = '在职' ORDER BY id"
        params = (f"%{keyword}%", f"%{keyword}%")
        return get_db().execute_query(sql, params)

    def add_coach(self, name, phone, gender, specialty, salary):
        sql = "INSERT INTO coach (name, phone, gender, specialty, salary) VALUES (%s, %s, %s, %s, %s)"
        return get_db().execute_update(sql, (name, phone, gender, specialty, salary))

    def update_coach(self, coach_id, name, phone, gender, specialty, salary):
        sql = """UPDATE coach
                 SET name = %s, phone = %s, gender = %s, specialty = %s, salary = %s
                 WHERE id = %s"""
        return get_db().execute_update(sql, (name, phone, gender, specialty, salary, coach_id))

    def delete_coach(self, coach_id):
        sql = "UPDATE coach SET status = '离职' WHERE id = %s"
        return get_db().execute_update(sql, (coach_id,))


class CourseService:
    """课程服务。"""

    def get_all_courses(self):
        sql = "SELECT * FROM course ORDER BY id"
        return get_db().execute_query(sql)

    def get_course_by_id(self, course_id):
        sql = "SELECT * FROM course WHERE id = %s"
        result = get_db().execute_query(sql, (course_id,))
        return result[0] if result else None

    def add_course(self, name, category, duration, max_capacity, description):
        sql = """INSERT INTO course (name, category, duration, max_capacity, description)
                 VALUES (%s, %s, %s, %s, %s)"""
        return get_db().execute_update(sql, (name, category, duration, max_capacity, description))

    def update_course(self, course_id, name, category, duration, max_capacity, description):
        sql = """UPDATE course
                 SET name = %s, category = %s, duration = %s, max_capacity = %s, description = %s
                 WHERE id = %s"""
        return get_db().execute_update(sql, (name, category, duration, max_capacity, description, course_id))

    def delete_course(self, course_id):
        sql = "DELETE FROM course WHERE id = %s"
        return get_db().execute_update(sql, (course_id,))


class CourseScheduleService:
    """课程安排服务。"""

    def get_all_schedules(self):
        sql = """SELECT cs.*, c.name AS course_name, c.category AS course_category, co.name AS coach_name
                 FROM course_schedule cs
                 JOIN course c ON cs.course_id = c.id
                 JOIN coach co ON cs.coach_id = co.id
                 ORDER BY cs.schedule_time DESC"""
        return get_db().execute_query(sql)

    def get_upcoming_schedules(self, days=7):
        self.refresh_schedule_status()
        sql = """SELECT cs.*, c.name AS course_name, c.category AS course_category, co.name AS coach_name
                 FROM course_schedule cs
                 JOIN course c ON cs.course_id = c.id
                 JOIN coach co ON cs.coach_id = co.id
                 WHERE cs.schedule_time >= NOW()
                   AND cs.schedule_time <= DATE_ADD(NOW(), INTERVAL %s DAY)
                   AND cs.status = '未开始'
                 ORDER BY cs.schedule_time"""
        return get_db().execute_query(sql, (days,))

    def get_schedule_by_id(self, schedule_id):
        sql = """SELECT cs.*, c.name AS course_name, c.category AS course_category, co.name AS coach_name
                 FROM course_schedule cs
                 JOIN course c ON cs.course_id = c.id
                 JOIN coach co ON cs.coach_id = co.id
                 WHERE cs.id = %s"""
        result = get_db().execute_query(sql, (schedule_id,))
        return result[0] if result else None

    def add_schedule(self, course_id, coach_id, schedule_time, room, max_capacity):
        sql = """INSERT INTO course_schedule (course_id, coach_id, schedule_time, room, max_capacity, status)
                 VALUES (%s, %s, %s, %s, %s, '未开始')"""
        return get_db().execute_update(sql, (course_id, coach_id, schedule_time, room, max_capacity))

    def update_schedule(self, schedule_id, course_id, coach_id, schedule_time, room, max_capacity):
        sql = """UPDATE course_schedule
                 SET course_id = %s, coach_id = %s, schedule_time = %s, room = %s, max_capacity = %s
                 WHERE id = %s"""
        return get_db().execute_update(sql, (course_id, coach_id, schedule_time, room, max_capacity, schedule_id))

    def delete_schedule(self, schedule_id):
        sql = "DELETE FROM course_schedule WHERE id = %s"
        return get_db().execute_update(sql, (schedule_id,))

    def refresh_schedule_status(self):
        get_db().call_procedure("sp_update_schedule_status")


class BookingService:
    """预约签到服务。"""

    def get_all_bookings(self):
        CourseScheduleService().refresh_schedule_status()
        sql = """SELECT b.*, m.name AS member_name, m.phone AS member_phone,
                        c.name AS course_name, cs.schedule_time
                 FROM booking b
                 JOIN member m ON b.member_id = m.id
                 JOIN course_schedule cs ON b.schedule_id = cs.id
                 JOIN course c ON cs.course_id = c.id
                 ORDER BY b.book_time DESC"""
        return get_db().execute_query(sql)

    def get_member_bookings(self, member_id):
        sql = """SELECT b.*, c.name AS course_name, cs.schedule_time, co.name AS coach_name
                 FROM booking b
                 JOIN course_schedule cs ON b.schedule_id = cs.id
                 JOIN course c ON cs.course_id = c.id
                 JOIN coach co ON cs.coach_id = co.id
                 WHERE b.member_id = %s
                 ORDER BY cs.schedule_time DESC"""
        return get_db().execute_query(sql, (member_id,))

    def get_schedule_bookings(self, schedule_id):
        sql = """SELECT b.*, m.name AS member_name, m.phone AS member_phone
                 FROM booking b
                 JOIN member m ON b.member_id = m.id
                 WHERE b.schedule_id = %s
                 ORDER BY b.book_time"""
        return get_db().execute_query(sql, (schedule_id,))

    def book_course(self, member_id, schedule_id):
        db = get_db()
        with db.transaction() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, status FROM booking WHERE member_id = %s AND schedule_id = %s",
                    (member_id, schedule_id),
                )
                existing = cursor.fetchone()
                if existing and existing["status"] in ("已预约", "已签到"):
                    raise ValueError("该课程已预约")

                cursor.execute(
                    """SELECT id, current_count, max_capacity, status, schedule_time
                       FROM course_schedule
                       WHERE id = %s
                       FOR UPDATE""",
                    (schedule_id,),
                )
                schedule = cursor.fetchone()
                if not schedule:
                    raise ValueError("课程不存在")
                if schedule["status"] != "未开始":
                    raise ValueError("该课程当前不可预约")
                if schedule["current_count"] >= schedule["max_capacity"]:
                    raise ValueError("课程名额已满")

                if existing and existing["status"] == "已取消":
                    cursor.execute(
                        """UPDATE booking
                           SET status = '已预约', book_time = NOW(), checkin_time = NULL, rating = NULL, remark = NULL
                           WHERE id = %s""",
                        (existing["id"],),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO booking (member_id, schedule_id) VALUES (%s, %s)",
                        (member_id, schedule_id),
                    )

                cursor.execute(
                    "UPDATE course_schedule SET current_count = current_count + 1 WHERE id = %s",
                    (schedule_id,),
                )
        return True

    def checkin_booking(self, booking_id):
        db = get_db()
        with db.transaction() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT b.id, b.status, b.checkin_time
                       FROM booking b
                       WHERE b.id = %s
                       FOR UPDATE""",
                    (booking_id,),
                )
                booking = cursor.fetchone()
                if not booking:
                    raise ValueError("预约不存在")
                if booking["status"] != "已预约" or booking["checkin_time"] is not None:
                    raise ValueError("签到失败，可能已签到或预约状态不允许")

                cursor.execute(
                    "UPDATE booking SET checkin_time = NOW(), status = '已签到' WHERE id = %s",
                    (booking_id,),
                )
        return True

    def cancel_booking(self, booking_id):
        db = get_db()
        with db.transaction() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, schedule_id, status FROM booking WHERE id = %s FOR UPDATE",
                    (booking_id,),
                )
                booking = cursor.fetchone()
                if not booking:
                    raise ValueError("预约不存在")
                if booking["status"] != "已预约":
                    raise ValueError("只有已预约状态的记录才能取消")

                cursor.execute("UPDATE booking SET status = '已取消' WHERE id = %s", (booking_id,))
                cursor.execute(
                    """UPDATE course_schedule
                       SET current_count = CASE
                           WHEN current_count > 0 THEN current_count - 1
                           ELSE 0
                       END
                       WHERE id = %s""",
                    (booking["schedule_id"],),
                )
        return True

    def rate_booking(self, booking_id, rating, remark):
        if rating < 1 or rating > 5:
            raise ValueError("评分必须在 1 到 5 之间")

        sql = """UPDATE booking
                 SET rating = %s, remark = %s
                 WHERE id = %s AND status = '已签到'"""
        affected = get_db().execute_update(sql, (rating, remark, booking_id))
        if affected == 0:
            raise ValueError("只有已签到的课程记录才能评价")
        return affected


class WeeklyStatsService:
    """课程统计服务。"""

    def get_weekly_stats(self):
        sql = "SELECT * FROM v_course_weekly_stats ORDER BY booking_count DESC"
        return get_db().execute_query(sql)
