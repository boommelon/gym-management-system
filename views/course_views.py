import tkinter as tk
from tkinter import messagebox, ttk

from services.course_service import BookingService, CoachService, CourseScheduleService, CourseService, WeeklyStatsService
from services.member_service import MemberCardService, MemberService
from views.common import WINDOW_BG, clear_tree, create_action_bar, create_section_title, create_table


class CoachManagerView:
    """教练管理视图。"""

    def __init__(self, parent):
        self.parent = parent
        self.service = CoachService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        create_section_title(self.parent, "教练管理")

        search_frame = tk.Frame(self.parent, bg=WINDOW_BG)
        search_frame.pack(fill=tk.X, padx=20)
        tk.Label(search_frame, text="搜索:", bg=WINDOW_BG).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="查询", command=self.search, width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="显示全部", command=self.load_data, width=8).pack(side=tk.LEFT)

        columns = ("编号", "姓名", "手机号", "性别", "专长", "月薪", "入职日期", "状态")
        widths = {"编号": 60, "姓名": 90, "手机号": 120, "专长": 180, "月薪": 90}
        self.tree = create_table(self.parent, columns, widths, height=15)

        btn_frame = create_action_bar(self.parent)
        tk.Button(btn_frame, text="添加教练", command=self.add_coach, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑教练", command=self.edit_coach, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除教练", command=self.delete_coach, width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        clear_tree(self.tree)
        for coach in self.service.get_all_coaches():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    coach["id"],
                    coach["name"],
                    coach["phone"],
                    coach["gender"],
                    coach.get("specialty", "") or "",
                    coach["salary"],
                    coach["hire_date"],
                    coach["status"],
                ),
            )

    def search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_data()
            return
        clear_tree(self.tree)
        for coach in self.service.search_coach(keyword):
            self.tree.insert(
                "",
                tk.END,
                values=(
                    coach["id"],
                    coach["name"],
                    coach["phone"],
                    coach["gender"],
                    coach.get("specialty", "") or "",
                    coach["salary"],
                    coach["hire_date"],
                    coach["status"],
                ),
            )

    def add_coach(self):
        self.open_dialog()

    def edit_coach(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的教练")
            return
        coach_id = self.tree.item(selection[0])["values"][0]
        self.open_dialog(self.service.get_coach_by_id(coach_id))

    def open_dialog(self, coach=None):
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑教练" if coach else "添加教练")
        dialog.geometry("420x320")
        dialog.transient(self.parent)
        dialog.grab_set()

        values = coach or {}
        entries = {}
        y = 20
        for text, key in [("姓名", "name"), ("手机号", "phone"), ("专长", "specialty"), ("月薪", "salary")]:
            tk.Label(dialog, text=f"{text}:").place(x=50, y=y)
            entry = tk.Entry(dialog, width=28)
            entry.place(x=130, y=y)
            entry.insert(0, str(values.get(key, "") or ""))
            entries[key] = entry
            y += 40

        tk.Label(dialog, text="性别:").place(x=50, y=y)
        gender_var = tk.StringVar(value=values.get("gender", "男"))
        tk.Radiobutton(dialog, text="男", variable=gender_var, value="男").place(x=130, y=y)
        tk.Radiobutton(dialog, text="女", variable=gender_var, value="女").place(x=190, y=y)

        def save():
            try:
                name = entries["name"].get().strip()
                phone = entries["phone"].get().strip()
                salary = float(entries["salary"].get().strip())
                specialty = entries["specialty"].get().strip() or None
                if not name or not phone:
                    raise ValueError("姓名和手机号不能为空")

                if coach:
                    self.service.update_coach(coach["id"], name, phone, gender_var.get(), specialty, salary)
                else:
                    self.service.add_coach(name, phone, gender_var.get(), specialty, salary)
                dialog.destroy()
                self.load_data()
                messagebox.showinfo("成功", "教练信息已保存")
            except Exception as exc:
                messagebox.showerror("错误", str(exc))

        tk.Button(dialog, text="保存", command=save, width=10).place(x=130, y=y + 50)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=240, y=y + 50)

    def delete_coach(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要删除的教练")
            return
        if not messagebox.askyesno("确认", "确定将该教练标记为离职吗？"):
            return
        coach_id = self.tree.item(selection[0])["values"][0]
        try:
            self.service.delete_coach(coach_id)
            self.load_data()
            messagebox.showinfo("成功", "教练状态已更新")
        except Exception as exc:
            messagebox.showerror("错误", str(exc))


class CourseManagerView:
    """课程与排课管理视图。"""

    def __init__(self, parent):
        self.parent = parent
        self.course_service = CourseService()
        self.schedule_service = CourseScheduleService()
        self.coach_service = CoachService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        create_section_title(self.parent, "课程管理")

        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.course_frame = tk.Frame(notebook, bg=WINDOW_BG)
        self.schedule_frame = tk.Frame(notebook, bg=WINDOW_BG)
        notebook.add(self.course_frame, text="课程类别")
        notebook.add(self.schedule_frame, text="课程安排")

        self.setup_course_tab()
        self.setup_schedule_tab()

    def setup_course_tab(self):
        columns = ("编号", "名称", "类别", "时长(分钟)", "最大人数", "描述")
        widths = {"编号": 60, "名称": 120, "类别": 100, "描述": 220}
        self.course_tree = create_table(self.course_frame, columns, widths)
        btn_frame = create_action_bar(self.course_frame)
        tk.Button(btn_frame, text="添加课程", command=self.add_course, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑课程", command=self.edit_course, width=12).pack(side=tk.LEFT, padx=5)

    def setup_schedule_tab(self):
        columns = ("编号", "课程", "教练", "上课时间", "教室", "人数上限", "已预约", "状态")
        widths = {"编号": 60, "课程": 120, "教练": 100, "上课时间": 160, "教室": 100}
        self.schedule_tree = create_table(self.schedule_frame, columns, widths)
        btn_frame = create_action_bar(self.schedule_frame)
        tk.Button(btn_frame, text="添加安排", command=self.add_schedule, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑安排", command=self.edit_schedule, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除安排", command=self.delete_schedule, width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        self.load_courses()
        self.load_schedules()

    def load_courses(self):
        clear_tree(self.course_tree)
        for course in self.course_service.get_all_courses():
            self.course_tree.insert(
                "",
                tk.END,
                values=(
                    course["id"],
                    course["name"],
                    course.get("category", "") or "",
                    course.get("duration", 60),
                    course.get("max_capacity", 20),
                    course.get("description", "") or "",
                ),
            )

    def load_schedules(self):
        clear_tree(self.schedule_tree)
        for schedule in self.schedule_service.get_all_schedules():
            self.schedule_tree.insert(
                "",
                tk.END,
                values=(
                    schedule["id"],
                    schedule["course_name"],
                    schedule["coach_name"],
                    schedule["schedule_time"],
                    schedule.get("room", "") or "",
                    schedule.get("max_capacity", 0),
                    schedule.get("current_count", 0),
                    schedule["status"],
                ),
            )

    def add_course(self):
        self.open_course_dialog()

    def edit_course(self):
        selection = self.course_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的课程")
            return
        course_id = self.course_tree.item(selection[0])["values"][0]
        self.open_course_dialog(self.course_service.get_course_by_id(course_id))

    def open_course_dialog(self, course=None):
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑课程" if course else "添加课程")
        dialog.geometry("430x320")
        dialog.transient(self.parent)
        dialog.grab_set()

        values = course or {}
        entries = {}
        y = 20
        for text, key in [("名称", "name"), ("类别", "category"), ("时长", "duration"), ("人数上限", "max_capacity"), ("描述", "description")]:
            tk.Label(dialog, text=f"{text}:").place(x=50, y=y)
            entry = tk.Entry(dialog, width=28)
            entry.place(x=140, y=y)
            entry.insert(0, str(values.get(key, "") or ""))
            entries[key] = entry
            y += 40

        def save():
            try:
                name = entries["name"].get().strip()
                if not name:
                    raise ValueError("课程名称不能为空")
                category = entries["category"].get().strip() or "综合训练"
                duration = int(entries["duration"].get().strip() or 60)
                max_capacity = int(entries["max_capacity"].get().strip() or 20)
                description = entries["description"].get().strip() or None

                if course:
                    self.course_service.update_course(course["id"], name, category, duration, max_capacity, description)
                else:
                    self.course_service.add_course(name, category, duration, max_capacity, description)
                dialog.destroy()
                self.load_courses()
                messagebox.showinfo("成功", "课程信息已保存")
            except Exception as exc:
                messagebox.showerror("错误", str(exc))

        tk.Button(dialog, text="保存", command=save, width=10).place(x=140, y=y + 20)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=250, y=y + 20)

    def add_schedule(self):
        self.open_schedule_dialog()

    def edit_schedule(self):
        selection = self.schedule_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的安排")
            return
        schedule_id = self.schedule_tree.item(selection[0])["values"][0]
        self.open_schedule_dialog(self.schedule_service.get_schedule_by_id(schedule_id))

    def open_schedule_dialog(self, schedule=None):
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑排课" if schedule else "添加排课")
        dialog.geometry("450x320")
        dialog.transient(self.parent)
        dialog.grab_set()

        courses = self.course_service.get_all_courses()
        coaches = self.coach_service.get_all_coaches()
        course_var = tk.StringVar()
        coach_var = tk.StringVar()

        tk.Label(dialog, text="课程:").place(x=50, y=30)
        ttk.Combobox(
            dialog,
            textvariable=course_var,
            values=[f"{item['id']}: {item['name']}" for item in courses],
            state="readonly",
            width=28,
        ).place(x=140, y=30)

        tk.Label(dialog, text="教练:").place(x=50, y=80)
        ttk.Combobox(
            dialog,
            textvariable=coach_var,
            values=[f"{item['id']}: {item['name']}" for item in coaches],
            state="readonly",
            width=28,
        ).place(x=140, y=80)

        tk.Label(dialog, text="上课时间:").place(x=50, y=130)
        time_entry = tk.Entry(dialog, width=30)
        time_entry.place(x=140, y=130)

        tk.Label(dialog, text="教室:").place(x=50, y=180)
        room_entry = tk.Entry(dialog, width=30)
        room_entry.place(x=140, y=180)

        tk.Label(dialog, text="人数上限:").place(x=50, y=230)
        capacity_entry = tk.Entry(dialog, width=30)
        capacity_entry.place(x=140, y=230)

        if schedule:
            for item in courses:
                if item["id"] == schedule["course_id"]:
                    course_var.set(f"{item['id']}: {item['name']}")
                    break
            for item in coaches:
                if item["id"] == schedule["coach_id"]:
                    coach_var.set(f"{item['id']}: {item['name']}")
                    break
            time_entry.insert(0, str(schedule["schedule_time"]))
            room_entry.insert(0, schedule.get("room", "") or "")
            capacity_entry.insert(0, str(schedule.get("max_capacity", 20)))
        else:
            capacity_entry.insert(0, "20")

        def save():
            try:
                if not course_var.get() or not coach_var.get() or not time_entry.get().strip():
                    raise ValueError("请填写完整的排课信息")
                course_id = int(course_var.get().split(":")[0])
                coach_id = int(coach_var.get().split(":")[0])
                schedule_time = time_entry.get().strip()
                room = room_entry.get().strip() or None
                max_capacity = int(capacity_entry.get().strip() or 20)

                if schedule:
                    self.schedule_service.update_schedule(
                        schedule["id"], course_id, coach_id, schedule_time, room, max_capacity
                    )
                else:
                    self.schedule_service.add_schedule(course_id, coach_id, schedule_time, room, max_capacity)
                dialog.destroy()
                self.load_schedules()
                messagebox.showinfo("成功", "课程安排已保存")
            except Exception as exc:
                messagebox.showerror("错误", str(exc))

        tk.Button(dialog, text="保存", command=save, width=10).place(x=140, y=270)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=250, y=270)

    def delete_schedule(self):
        selection = self.schedule_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要删除的安排")
            return
        if not messagebox.askyesno("确认", "确定删除该课程安排吗？"):
            return

        schedule_id = self.schedule_tree.item(selection[0])["values"][0]
        try:
            self.schedule_service.delete_schedule(schedule_id)
            self.load_schedules()
            messagebox.showinfo("成功", "课程安排已删除")
        except Exception as exc:
            messagebox.showerror("错误", str(exc))


class BookingManagerView:
    """课程预约、签到与评价视图。"""

    def __init__(self, parent):
        self.parent = parent
        self.member_service = MemberService()
        self.member_card_service = MemberCardService()
        self.booking_service = BookingService()
        self.schedule_service = CourseScheduleService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        create_section_title(self.parent, "预约与签到")

        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.booking_frame = tk.Frame(notebook, bg=WINDOW_BG)
        self.checkin_frame = tk.Frame(notebook, bg=WINDOW_BG)
        notebook.add(self.booking_frame, text="预约管理")
        notebook.add(self.checkin_frame, text="签到评价")

        self.setup_booking_tab()
        self.setup_checkin_tab()

    def setup_booking_tab(self):
        columns = ("编号", "会员姓名", "手机号", "课程", "上课时间", "预约时间", "状态")
        widths = {"编号": 60, "会员姓名": 90, "手机号": 120, "课程": 120, "上课时间": 160}
        self.booking_tree = create_table(self.booking_frame, columns, widths)
        btn_frame = create_action_bar(self.booking_frame)
        tk.Button(btn_frame, text="课程预约", command=self.open_booking_dialog, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消预约", command=self.cancel_booking, width=12).pack(side=tk.LEFT, padx=5)

    def setup_checkin_tab(self):
        columns = ("编号", "会员姓名", "手机号", "课程", "上课时间", "预约时间", "签到时间", "状态")
        widths = {"编号": 60, "会员姓名": 90, "手机号": 120, "课程": 120, "上课时间": 160, "签到时间": 160}
        self.checkin_tree = create_table(self.checkin_frame, columns, widths)
        btn_frame = create_action_bar(self.checkin_frame)
        tk.Button(btn_frame, text="会员签到", command=self.checkin, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="课程评价", command=self.open_rating_dialog, width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        self.load_bookings()
        self.load_checkins()

    def load_bookings(self):
        clear_tree(self.booking_tree)
        for booking in self.booking_service.get_all_bookings():
            self.booking_tree.insert(
                "",
                tk.END,
                values=(
                    booking["id"],
                    booking["member_name"],
                    booking["member_phone"],
                    booking["course_name"],
                    booking["schedule_time"],
                    booking["book_time"],
                    booking["status"],
                ),
            )

    def load_checkins(self):
        clear_tree(self.checkin_tree)
        for booking in self.booking_service.get_all_bookings():
            self.checkin_tree.insert(
                "",
                tk.END,
                values=(
                    booking["id"],
                    booking["member_name"],
                    booking["member_phone"],
                    booking["course_name"],
                    booking["schedule_time"],
                    booking["book_time"],
                    booking.get("checkin_time", "") or "",
                    booking["status"],
                ),
            )

    def open_booking_dialog(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("课程预约")
        dialog.geometry("480x280")
        dialog.transient(self.parent)
        dialog.grab_set()

        members = self.member_service.get_all_members()
        schedules = self.schedule_service.get_upcoming_schedules(30)
        member_var = tk.StringVar()
        schedule_var = tk.StringVar()
        card_summary_var = tk.StringVar(value="请先选择会员")

        tk.Label(dialog, text="选择会员:").place(x=50, y=40)
        member_combo = ttk.Combobox(
            dialog,
            textvariable=member_var,
            values=[f"{item['id']}: {item['name']} ({item['phone']})" for item in members],
            state="readonly",
            width=32,
        )
        member_combo.place(x=150, y=40)

        tk.Label(dialog, text="会员卡信息:").place(x=50, y=90)
        tk.Label(dialog, textvariable=card_summary_var, bg=WINDOW_BG, fg="#7f8c8d").place(x=150, y=90)

        tk.Label(dialog, text="选择课程:").place(x=50, y=140)
        ttk.Combobox(
            dialog,
            textvariable=schedule_var,
            values=[f"{item['id']}: {item['course_name']} - {item['coach_name']} ({item['schedule_time']})" for item in schedules],
            state="readonly",
            width=32,
        ).place(x=150, y=140)

        def update_summary(_event=None):
            if not member_var.get():
                card_summary_var.set("请先选择会员")
                return
            member_id = int(member_var.get().split(":")[0])
            summary = self.member_card_service.get_member_card_summary(member_id)
            card_summary_var.set(summary["summary"])

        member_combo.bind("<<ComboboxSelected>>", update_summary)

        def save():
            try:
                if not member_var.get() or not schedule_var.get():
                    raise ValueError("请选择会员和课程安排")
                member_id = int(member_var.get().split(":")[0])
                schedule_id = int(schedule_var.get().split(":")[0])
                summary = self.member_card_service.get_member_card_summary(member_id)
                if not summary["has_valid_card"]:
                    raise ValueError("该会员没有可用会员卡，无法预约课程")
                self.booking_service.book_course(member_id, schedule_id)
                dialog.destroy()
                self.load_data()
                messagebox.showinfo("成功", "课程预约成功")
            except Exception as exc:
                messagebox.showerror("错误", str(exc))

        tk.Button(dialog, text="预约", command=save, width=10).place(x=150, y=210)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=260, y=210)

    def cancel_booking(self):
        selection = self.booking_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要取消的预约")
            return
        booking_id = self.booking_tree.item(selection[0])["values"][0]
        try:
            self.booking_service.cancel_booking(booking_id)
            self.load_data()
            messagebox.showinfo("成功", "预约已取消")
        except Exception as exc:
            messagebox.showerror("错误", str(exc))

    def checkin(self):
        selection = self.checkin_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要签到的记录")
            return
        item = self.checkin_tree.item(selection[0])["values"]
        booking_id = item[0]
        status = item[7]
        if status != "已预约":
            messagebox.showwarning("提示", "只有已预约状态的记录才能签到")
            return
        try:
            self.booking_service.checkin_booking(booking_id)
            self.load_data()
            messagebox.showinfo("成功", "签到成功，系统已自动处理会员卡次数或有效期")
        except Exception as exc:
            messagebox.showerror("错误", str(exc))

    def open_rating_dialog(self):
        selection = self.checkin_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要评价的记录")
            return
        item = self.checkin_tree.item(selection[0])["values"]
        booking_id = item[0]
        status = item[7]
        if status != "已签到":
            messagebox.showwarning("提示", "只有已签到的课程记录才能评价")
            return

        dialog = tk.Toplevel(self.parent)
        dialog.title("课程评价")
        dialog.geometry("320x240")
        dialog.transient(self.parent)
        dialog.grab_set()

        tk.Label(dialog, text="评分:").pack(pady=20)
        rating_var = tk.IntVar(value=5)
        for score in range(1, 6):
            tk.Radiobutton(dialog, text=f"{score} 星", variable=rating_var, value=score).pack()

        tk.Label(dialog, text="评价备注:").pack(pady=10)
        remark_entry = tk.Entry(dialog, width=30)
        remark_entry.pack()

        def save():
            try:
                self.booking_service.rate_booking(booking_id, rating_var.get(), remark_entry.get().strip() or None)
                dialog.destroy()
                messagebox.showinfo("成功", "评价已提交")
            except Exception as exc:
                messagebox.showerror("错误", str(exc))

        tk.Button(dialog, text="提交", command=save, width=10).pack(pady=16)


class ReportViewer:
    """统计报表视图。"""

    def __init__(self, parent):
        self.parent = parent
        self.stats_service = WeeklyStatsService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        create_section_title(self.parent, "课程预约统计报表")
        tk.Label(self.parent, text="展示近一周课程预约人数、签到人数与签到率", bg=WINDOW_BG, fg="#7f8c8d").pack()

        columns = ("课程ID", "课程名称", "类别", "安排次数", "预约人数", "签到人数", "签到率")
        widths = {"课程ID": 70, "课程名称": 140, "类别": 100, "签到率": 90}
        self.tree = create_table(self.parent, columns, widths, height=15)

        btn_frame = create_action_bar(self.parent)
        tk.Button(btn_frame, text="刷新数据", command=self.load_data, width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        clear_tree(self.tree)
        try:
            for stat in self.stats_service.get_weekly_stats():
                rate = stat.get("checkin_rate", 0) or 0
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        stat["course_id"],
                        stat["course_name"],
                        stat["course_category"],
                        stat.get("total_schedules", 0),
                        stat.get("booking_count", 0),
                        stat.get("checkin_count", 0),
                        f"{rate}%",
                    ),
                )
        except Exception as exc:
            messagebox.showerror("错误", f"加载报表失败: {exc}")


class ConsumptionQueryView:
    """会员消费与历史查询视图。"""

    def __init__(self, parent):
        self.parent = parent
        self.member_service = MemberService()
        self.card_service = MemberCardService()
        self.setup_ui()

    def setup_ui(self):
        create_section_title(self.parent, "会员消费查询")

        select_frame = tk.Frame(self.parent, bg=WINDOW_BG)
        select_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(select_frame, text="选择会员:", bg=WINDOW_BG).pack(side=tk.LEFT)
        self.member_var = tk.StringVar()
        members = self.member_service.get_all_members()
        combo = ttk.Combobox(
            select_frame,
            textvariable=self.member_var,
            values=[f"{item['id']}: {item['name']} ({item['phone']})" for item in members],
            state="readonly",
            width=30,
        )
        combo.pack(side=tk.LEFT, padx=10)
        combo.bind("<<ComboboxSelected>>", lambda _event: self.query())
        tk.Button(select_frame, text="查询", command=self.query, width=10).pack(side=tk.LEFT, padx=10)

        self.result_text = tk.Text(self.parent, width=90, height=22, font=("Microsoft YaHei UI", 10), bg="white")
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def query(self):
        if not self.member_var.get():
            return
        member_id = int(self.member_var.get().split(":")[0])
        self.result_text.delete(1.0, tk.END)
        try:
            results = self.card_service.get_member_consumption(member_id)
            if not results:
                self.result_text.insert(tk.END, "未查询到该会员的消费信息。\n")
                return

            current_type = None
            for row in results:
                info_type = row.get("info_type", "")
                if info_type != current_type:
                    self.result_text.insert(tk.END, f"\n{'=' * 40}\n")
                    self.result_text.insert(tk.END, f"【{info_type}】\n")
                    self.result_text.insert(tk.END, f"{'=' * 40}\n")
                    current_type = info_type
                self.result_text.insert(
                    tk.END,
                    f"{row.get('info_detail', '')}: {row.get('info_value', '')}\n",
                )
        except Exception as exc:
            self.result_text.insert(tk.END, f"查询失败: {exc}\n")
