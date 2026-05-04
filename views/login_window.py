import tkinter as tk
from tkinter import messagebox

from services.auth_service import AuthService
from views.common import TEXT_FONT, WINDOW_BG


class LoginWindow:
    """简单登录窗口。"""

    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.auth_service = AuthService()
        self.username_var = tk.StringVar(value="admin")
        self.password_var = tk.StringVar()
        self.setup_ui()

    def setup_ui(self):
        self.root.title("系统登录")
        self.root.geometry("520x380")
        self.root.minsize(520, 380)
        self.root.resizable(False, False)
        self.root.configure(bg=WINDOW_BG)

        outer = tk.Frame(self.root, bg=WINDOW_BG)
        outer.pack(fill=tk.BOTH, expand=True, padx=26, pady=26)

        card = tk.Frame(outer, bg="white", bd=1, relief=tk.SOLID)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            card,
            text="健身房会员及课程管理系统",
            font=("Microsoft YaHei UI", 21, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(pady=(30, 10))

        tk.Label(
            card,
            text="管理员登录",
            font=("Microsoft YaHei UI", 11),
            bg="white",
            fg="#7f8c8d",
        ).pack(pady=(0, 24))

        form = tk.Frame(card, bg="white")
        form.pack(fill=tk.X, padx=54)
        form.columnconfigure(0, weight=1)

        tk.Label(form, text="用户名", font=TEXT_FONT, bg="white", anchor="w").grid(
            row=0, column=0, sticky="ew", pady=(0, 6)
        )
        username_entry = tk.Entry(form, textvariable=self.username_var, font=("Microsoft YaHei UI", 12))
        username_entry.grid(row=1, column=0, sticky="ew", ipady=7, pady=(0, 18))

        tk.Label(form, text="密码", font=TEXT_FONT, bg="white", anchor="w").grid(
            row=2, column=0, sticky="ew", pady=(0, 6)
        )
        password_entry = tk.Entry(
            form,
            textvariable=self.password_var,
            font=("Microsoft YaHei UI", 12),
            show="*",
        )
        password_entry.grid(row=3, column=0, sticky="ew", ipady=7, pady=(0, 24))

        tk.Button(
            card,
            text="登录",
            command=self.handle_login,
            font=("Microsoft YaHei UI", 11),
            bg="#1abc9c",
            fg="white",
            activebackground="#16a085",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=28,
            pady=9,
        ).pack(pady=(0, 28))

        tk.Label(
            card,
            text="默认账号：admin    默认密码：123456",
            font=("Microsoft YaHei UI", 9),
            bg="white",
            fg="#95a5a6",
        ).pack(pady=(0, 18))

        self.root.bind("<Return>", lambda event: self.handle_login())
        username_entry.focus_set()

    def handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码。")
            return

        try:
            admin = self.auth_service.validate_admin(username, password)
        except Exception as exc:
            messagebox.showerror("数据库连接失败", f"无法连接数据库：{exc}")
            return

        if not admin:
            messagebox.showerror("登录失败", "用户名或密码错误。")
            self.password_var.set("")
            return

        self.on_success(admin)
