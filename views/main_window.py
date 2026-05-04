import tkinter as tk

from views.common import WINDOW_BG
from views.course_views import (
    BookingManagerView,
    CoachManagerView,
    ConsumptionQueryView,
    CourseManagerView,
    ReportViewer,
)
from views.equipment_views import EquipmentManagerView
from views.login_window import LoginWindow
from views.member_views import CardManagerView, MemberManagerView


class MainWindow:
    """应用主窗口，只负责导航和内容切换。"""

    def __init__(self, root, admin_info=None):
        self.root = root
        self.admin_info = admin_info or {}
        self.root.title("健身房会员及课程管理系统")
        self.root.geometry("1200x760")
        self.root.configure(bg=WINDOW_BG)
        self.current_view = None
        self.setup_ui()

    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text="健身房会员及课程管理系统",
            font=("Microsoft YaHei UI", 22, "bold"),
            fg="white",
            bg="#2c3e50",
        ).pack(pady=12)

        admin_name = self.admin_info.get("name") or self.admin_info.get("username") or "admin"
        tk.Label(
            title_frame,
            text=f"管理员：{admin_name}",
            font=("Microsoft YaHei UI", 10),
            fg="#dfe6e9",
            bg="#2c3e50",
        ).place(relx=0.98, rely=0.5, anchor="e")

        body_frame = tk.Frame(self.root, bg=WINDOW_BG)
        body_frame.pack(fill=tk.BOTH, expand=True)

        self.menu_frame = tk.Frame(body_frame, bg="#34495e", width=220)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.menu_frame.pack_propagate(False)

        self.content_frame = tk.Frame(body_frame, bg=WINDOW_BG)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.menu_items = [
            ("会员管理", MemberManagerView),
            ("会员卡管理", CardManagerView),
            ("教练管理", CoachManagerView),
            ("课程管理", CourseManagerView),
            ("预约签到", BookingManagerView),
            ("器材管理", EquipmentManagerView),
            ("数据报表", ReportViewer),
            ("消费查询", ConsumptionQueryView),
        ]

        for text, view_class in self.menu_items:
            tk.Button(
                self.menu_frame,
                text=text,
                command=lambda target=view_class: self.open_view(target),
                font=("Microsoft YaHei UI", 11),
                bg="#34495e",
                fg="white",
                activebackground="#1abc9c",
                activeforeground="white",
                relief=tk.FLAT,
                pady=12,
                cursor="hand2",
            ).pack(fill=tk.X, padx=12, pady=3)

        self.show_welcome()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_welcome(self):
        self.clear_content()
        tk.Label(
            self.content_frame,
            text="欢迎使用健身房会员及课程管理系统",
            font=("Microsoft YaHei UI", 24, "bold"),
            bg=WINDOW_BG,
            fg="#2c3e50",
        ).pack(pady=120)
        tk.Label(
            self.content_frame,
            text="当前版本提供会员、课程、预约、器材、报表和消费查询等基础功能。",
            font=("Microsoft YaHei UI", 11),
            bg=WINDOW_BG,
            fg="#7f8c8d",
        ).pack()

    def open_view(self, view_class):
        self.clear_content()
        self.current_view = view_class(self.content_frame)


def run():
    root = tk.Tk()

    def open_main_window(admin_info):
        for widget in root.winfo_children():
            widget.destroy()
        root.unbind("<Return>")
        MainWindow(root, admin_info)

    LoginWindow(root, open_main_window)
    root.mainloop()


if __name__ == "__main__":
    run()
