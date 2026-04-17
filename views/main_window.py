import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.member_service import MemberService, CardTypeService, MemberCardService
from services.course_service import CoachService, CourseService, CourseScheduleService, BookingService, WeeklyStatsService
from services.equipment_service import EquipmentService, EquipmentBorrowService


class MainWindow:
    """主窗口"""

    def __init__(self, root):
        self.root = root
        self.root.title("健身房会员及课程管理系统")
        self.root.geometry("1200x700")

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 顶部标题
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)

        tk.Label(title_frame, text="健身房会员及课程管理系统",
                font=("微软雅黑", 22, "bold"), fg="white", bg="#2c3e50").pack(pady=15)

        # 左侧菜单
        menu_frame = tk.Frame(self.root, bg="#34495e", width=200)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        menu_frame.pack_propagate(False)

        # 功能按钮
        buttons = [
            ("会员管理", self.open_member_manager),
            ("会员卡管理", self.open_card_manager),
            ("教练管理", self.open_coach_manager),
            ("课程管理", self.open_course_manager),
            ("预约签到", self.open_booking_manager),
            ("器材管理", self.open_equipment_manager),
            ("数据报表", self.open_report_viewer),
            ("消费查询", self.open_consumption_query),
        ]

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(menu_frame, text=text, command=command,
                          font=("微软雅黑", 12), bg="#34495e", fg="white",
                          activebackground="#1abc9c", activeforeground="white",
                          relief=tk.FLAT, pady=12, cursor="hand2")
            btn.pack(fill=tk.X, padx=10, pady=2)

        # 右侧内容区
        self.content_frame = tk.Frame(self.root, bg="#ecf0f1")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 默认显示欢迎页
        self.show_welcome()

    def show_welcome(self):
        """显示欢迎页面"""
        self.clear_content()

        welcome_label = tk.Label(self.content_frame,
                                text="欢迎使用健身房会员及课程管理系统",
                                font=("微软雅黑", 24), bg="#ecf0f1", fg="#2c3e50")
        welcome_label.pack(pady=100)

        info_label = tk.Label(self.content_frame,
                             text="请从左侧菜单选择功能模块",
                             font=("微软雅黑", 14), bg="#ecf0f1", fg="#7f8c8d")
        info_label.pack()

    def clear_content(self):
        """清空内容区"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def open_member_manager(self):
        """打开会员管理"""
        self.clear_content()
        MemberManagerView(self.content_frame)

    def open_card_manager(self):
        """打开会员卡管理"""
        self.clear_content()
        CardManagerView(self.content_frame)

    def open_coach_manager(self):
        """打开教练管理"""
        self.clear_content()
        CoachManagerView(self.content_frame)

    def open_course_manager(self):
        """打开课程管理"""
        self.clear_content()
        CourseManagerView(self.content_frame)

    def open_booking_manager(self):
        """打开预约签到"""
        self.clear_content()
        BookingManagerView(self.content_frame)

    def open_equipment_manager(self):
        """打开器材管理"""
        self.clear_content()
        EquipmentManagerView(self.content_frame)

    def open_report_viewer(self):
        """打开数据报表"""
        self.clear_content()
        ReportViewer(self.content_frame)

    def open_consumption_query(self):
        """打开消费查询"""
        self.clear_content()
        ConsumptionQueryView(self.content_frame)


class MemberManagerView:
    """会员管理视图"""

    def __init__(self, parent):
        self.parent = parent
        self.service = MemberService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置UI"""
        # 标题
        tk.Label(self.parent, text="会员管理", font=("微软雅黑", 18, "bold"),
                bg="#ecf0f1").pack(pady=10)

        # 搜索栏
        search_frame = tk.Frame(self.parent, bg="#ecf0f1")
        search_frame.pack(fill=tk.X, padx=20)

        tk.Label(search_frame, text="搜索:", bg="#ecf0f1").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="查询", command=self.search,
                 width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="显示全部", command=self.load_data,
                 width=8).pack(side=tk.LEFT)

        # 表格
        table_frame = tk.Frame(self.parent, bg="#ecf0f1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("编号", "姓名", "手机号", "性别", "入会日期", "状态", "备注")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮区
        btn_frame = tk.Frame(self.parent, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="添加会员", command=self.add_member,
                 width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑会员", command=self.edit_member,
                 width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除会员", command=self.delete_member,
                 width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        """加载数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        members = self.service.get_all_members()
        for m in members:
            self.tree.insert("", tk.END, values=(
                m['id'], m['name'], m['phone'], m['gender'],
                m['join_date'], m['status'], m.get('remark', '')
            ))

    def search(self):
        """搜索"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_data()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        members = self.service.search_member(keyword)
        for m in members:
            self.tree.insert("", tk.END, values=(
                m['id'], m['name'], m['phone'], m['gender'],
                m['join_date'], m['status'], m.get('remark', '')
            ))

    def add_member(self):
        """添加会员"""
        self.open_member_dialog()

    def edit_member(self):
        """编辑会员"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的会员")
            return

        item = self.tree.item(selection[0])
        member_id = item['values'][0]
        member = self.service.get_member_by_id(member_id)
        self.open_member_dialog(member)

    def open_member_dialog(self, member=None):
        """打开会员对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("会员信息" if member else "添加会员")
        dialog.geometry("400x400")
        dialog.transient(self.parent)
        dialog.grab_set()

        fields = [
            ("姓名:", "name"),
            ("手机号:", "phone"),
            ("性别:", "gender"),
            ("身份证号:", "id_card"),
            ("状态:", "status"),
            ("备注:", "remark"),
        ]

        entries = {}
        y = 20

        # 预填值
        values = {}
        if member:
            values = {
                'name': member.get('name', ''),
                'phone': member.get('phone', ''),
                'gender': member.get('gender', '男'),
                'id_card': member.get('id_card', ''),
                'status': member.get('status', '正常'),
                'remark': member.get('remark', ''),
            }

        for label_text, field_name in fields:
            tk.Label(dialog, text=label_text).place(x=50, y=y)

            if field_name == "gender":
                var = tk.StringVar(value=values.get('gender', '男'))
                entries[field_name] = var
                tk.Radiobutton(dialog, text="男", variable=var, value="男").place(x=120, y=y)
                tk.Radiobutton(dialog, text="女", variable=var, value="女").place(x=170, y=y)
            elif field_name == "status":
                var = tk.StringVar(value=values.get('status', '正常'))
                entries[field_name] = var
                tk.Radiobutton(dialog, text="正常", variable=var, value="正常").place(x=120, y=y)
                tk.Radiobutton(dialog, text="冻结", variable=var, value="冻结").place(x=180, y=y)
                tk.Radiobutton(dialog, text="已过期", variable=var, value="已过期").place(x=240, y=y)
            else:
                entry = tk.Entry(dialog, width=25)
                entry.place(x=120, y=y)
                if field_name in values:
                    entry.insert(0, values[field_name])
                entries[field_name] = entry

            y += 40

        def save():
            try:
                name = entries['name'].get().strip()
                phone = entries['phone'].get().strip()
                gender = entries['gender'].get()
                id_card = entries['id_card'].get().strip() or None
                status = entries['status'].get()
                remark = entries['remark'].get().strip() or None

                if not name or not phone:
                    messagebox.showerror("错误", "姓名和手机号不能为空")
                    return

                if member:
                    self.service.update_member(member['id'], name, phone, gender, id_card, remark, status)
                    messagebox.showinfo("成功", "会员信息已更新")
                else:
                    self.service.add_member(name, phone, gender, id_card, remark)
                    messagebox.showinfo("成功", "会员添加成功")

                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        tk.Button(dialog, text="保存", command=save, width=10).place(x=120, y=y+20)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=220, y=y+20)

    def delete_member(self):
        """删除会员"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要删除的会员")
            return

        if not messagebox.askyesno("确认", "确定要删除该会员吗？"):
            return

        item = self.tree.item(selection[0])
        member_id = item['values'][0]

        try:
            self.service.delete_member(member_id)
            messagebox.showinfo("成功", "会员已删除")
            self.load_data()
        except Exception as e:
            messagebox.showerror("错误", str(e))


class CardManagerView:
    """会员卡管理视图"""

    def __init__(self, parent):
        self.parent = parent
        self.member_service = MemberService()
        self.card_type_service = CardTypeService()
        self.member_card_service = MemberCardService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置UI"""
        tk.Label(self.parent, text="会员卡管理", font=("微软雅黑", 18, "bold"),
                bg="#ecf0f1").pack(pady=10)

        # 选项卡
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 卡类型管理
        self.card_type_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(self.card_type_frame, text="卡类型管理")
        self.setup_card_type_tab()

        # 会员卡办理
        self.member_card_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(self.member_card_frame, text="会员卡办理")
        self.setup_member_card_tab()

    def setup_card_type_tab(self):
        """设置卡类型选项卡"""
        # 表格
        table_frame = tk.Frame(self.card_type_frame, bg="#ecf0f1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("编号", "名称", "类别", "限制次数", "有效期(天)", "价格", "描述")
        self.card_type_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.card_type_tree.heading(col, text=col)
            self.card_type_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.card_type_tree.yview)
        self.card_type_tree.configure(yscrollcommand=scrollbar.set)

        self.card_type_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮
        btn_frame = tk.Frame(self.card_type_frame, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="添加卡类型", command=self.add_card_type, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑卡类型", command=self.edit_card_type, width=12).pack(side=tk.LEFT, padx=5)

    def setup_member_card_tab(self):
        """设置会员卡办理选项卡"""
        # 表格
        table_frame = tk.Frame(self.member_card_frame, bg="#ecf0f1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("编号", "会员姓名", "会员手机", "卡类型", "购买日期", "有效期至", "剩余次数", "状态", "价格")
        self.member_card_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.member_card_tree.heading(col, text=col)

        self.member_card_tree.column("编号", width=50)
        self.member_card_tree.column("会员姓名", width=80)
        self.member_card_tree.column("会员手机", width=100)
        self.member_card_tree.column("卡类型", width=80)
        self.member_card_tree.column("状态", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.member_card_tree.yview)
        self.member_card_tree.configure(yscrollcommand=scrollbar.set)

        self.member_card_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮
        btn_frame = tk.Frame(self.member_card_frame, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="办理新卡", command=self.open_buy_card_dialog, width=12).pack(side=tk.LEFT, padx=5)

    def load_card_types(self):
        """加载卡类型数据"""
        for item in self.card_type_tree.get_children():
            self.card_type_tree.delete(item)

        card_types = self.card_type_service.get_all_card_types()
        for ct in card_types:
            self.card_type_tree.insert("", tk.END, values=(
                ct['id'], ct['name'], ct['card_category'],
                ct.get('times_limit', ''), ct.get('valid_days', ''),
                ct['price'], ct.get('description', '')
            ))

    def load_member_cards(self):
        """加载会员卡数据"""
        for item in self.member_card_tree.get_children():
            self.member_card_tree.delete(item)

        cards = self.member_card_service.get_all_member_cards()
        for c in cards:
            expire = c.get('expire_date', '') or ''
            remain = c.get('remain_times', '') or ''
            self.member_card_tree.insert("", tk.END, values=(
                c['id'], c['member_name'], c['member_phone'],
                c['card_type_name'], c['buy_date'], expire, remain,
                c['status'], c['price']
            ))

    def load_data(self):
        """加载数据"""
        self.load_card_types()
        self.load_member_cards()

    def add_card_type(self):
        """添加卡类型"""
        self.open_card_type_dialog()

    def edit_card_type(self):
        """编辑卡类型"""
        selection = self.card_type_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的卡类型")
            return

        item = self.card_type_tree.item(selection[0])
        card_type_id = item['values'][0]
        card_type = self.card_type_service.get_card_type_by_id(card_type_id)
        self.open_card_type_dialog(card_type)

    def open_card_type_dialog(self, card_type=None):
        """打开卡类型对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("卡类型信息" if card_type else "添加卡类型")
        dialog.geometry("400x400")
        dialog.transient(self.parent)
        dialog.grab_set()

        y = 20

        fields = [
            ("名称:", "name"),
            ("类别:", "category"),
            ("限制次数:", "times_limit"),
            ("有效期(天):", "valid_days"),
            ("价格:", "price"),
            ("描述:", "description"),
        ]

        entries = {}

        values = {}
        if card_type:
            values = {
                'name': card_type.get('name', ''),
                'category': card_type.get('card_category', '月卡'),
                'times_limit': str(card_type.get('times_limit', '')),
                'valid_days': str(card_type.get('valid_days', '')),
                'price': str(card_type.get('price', '')),
                'description': card_type.get('description', ''),
            }

        for label_text, field_name in fields:
            tk.Label(dialog, text=label_text).place(x=50, y=y)

            if field_name == "category":
                var = tk.StringVar(value=values.get('category', '月卡'))
                entries[field_name] = var
                for i, opt in enumerate(['次卡', '月卡', '季卡', '年卡']):
                    tk.Radiobutton(dialog, text=opt, variable=var, value=opt).place(x=120 + i*70, y=y)
            else:
                entry = tk.Entry(dialog, width=25)
                entry.place(x=120, y=y)
                if field_name in values:
                    entry.insert(0, values[field_name])
                entries[field_name] = entry

            y += 40

        def save():
            try:
                name = entries['name'].get().strip()
                category = entries['category'].get()
                times_limit = entries['times_limit'].get().strip()
                valid_days = entries['valid_days'].get().strip()
                price = entries['price'].get().strip()
                description = entries['description'].get().strip() or None

                if not name or not price:
                    messagebox.showerror("错误", "名称和价格不能为空")
                    return

                times_limit = int(times_limit) if times_limit else None
                valid_days = int(valid_days) if valid_days else None
                price = float(price)

                if card_type:
                    self.card_type_service.update_card_type(card_type['id'], name, category, times_limit, valid_days, price, description)
                    messagebox.showinfo("成功", "卡类型已更新")
                else:
                    self.card_type_service.add_card_type(name, category, times_limit, valid_days, price, description)
                    messagebox.showinfo("成功", "卡类型添加成功")

                dialog.destroy()
                self.load_card_types()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        tk.Button(dialog, text="保存", command=save, width=10).place(x=120, y=y+20)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=220, y=y+20)

    def open_buy_card_dialog(self):
        """打开办卡对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("办理会员卡")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()

        y = 20

        # 会员选择
        tk.Label(dialog, text="选择会员:").place(x=50, y=y)
        members = self.member_service.get_all_members()
        member_names = [f"{m['id']}: {m['name']} ({m['phone']})" for m in members]
        self.member_var = tk.StringVar()
        member_combo = ttk.Combobox(dialog, textvariable=self.member_var, values=member_names, width=25, state="readonly")
        member_combo.place(x=130, y=y)

        y += 40

        # 卡类型选择
        tk.Label(dialog, text="选择卡类型:").place(x=50, y=y)
        card_types = self.card_type_service.get_all_card_types()
        card_type_info = [f"{ct['id']}: {ct['name']} (¥{ct['price']})" for ct in card_types]
        self.card_type_var = tk.StringVar()
        card_type_combo = ttk.Combobox(dialog, textvariable=self.card_type_var, values=card_type_info, width=25, state="readonly")
        card_type_combo.place(x=130, y=y)

        def save():
            try:
                member_str = self.member_var.get()
                card_type_str = self.card_type_var.get()

                if not member_str or not card_type_str:
                    messagebox.showerror("错误", "请选择会员和卡类型")
                    return

                member_id = int(member_str.split(':')[0])
                card_type_id = int(card_type_str.split(':')[0])

                card_type = self.card_type_service.get_card_type_by_id(card_type_id)
                self.member_card_service.add_member_card(member_id, card_type_id, card_type['price'])

                messagebox.showinfo("成功", "会员卡办理成功")
                dialog.destroy()
                self.load_member_cards()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        tk.Button(dialog, text="办理", command=save, width=10).place(x=120, y=y+40)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=220, y=y+40)


class CoachManagerView:
    """教练管理视图"""

    def __init__(self, parent):
        self.parent = parent
        self.service = CoachService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置UI"""
        tk.Label(self.parent, text="教练管理", font=("微软雅黑", 18, "bold"),
                bg="#ecf0f1").pack(pady=10)

        # 搜索栏
        search_frame = tk.Frame(self.parent, bg="#ecf0f1")
        search_frame.pack(fill=tk.X, padx=20)

        tk.Label(search_frame, text="搜索:", bg="#ecf0f1").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="查询", command=self.search, width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="显示全部", command=self.load_data, width=8).pack(side=tk.LEFT)

        # 表格
        table_frame = tk.Frame(self.parent, bg="#ecf0f1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("编号", "姓名", "手机号", "性别", "专长", "月薪", "入职日期", "状态")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮
        btn_frame = tk.Frame(self.parent, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="添加教练", command=self.add_coach, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑教练", command=self.edit_coach, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除教练", command=self.delete_coach, width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        """加载数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        coaches = self.service.get_all_coaches()
        for c in coaches:
            self.tree.insert("", tk.END, values=(
                c['id'], c['name'], c['phone'], c['gender'],
                c.get('specialty', ''), c['salary'], c['hire_date'], c['status']
            ))

    def search(self):
        """搜索"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_data()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        coaches = self.service.search_coach(keyword)
        for c in coaches:
            self.tree.insert("", tk.END, values=(
                c['id'], c['name'], c['phone'], c['gender'],
                c.get('specialty', ''), c['salary'], c['hire_date'], c['status']
            ))

    def add_coach(self):
        """添加教练"""
        self.open_coach_dialog()

    def edit_coach(self):
        """编辑教练"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的教练")
            return

        item = self.tree.item(selection[0])
        coach_id = item['values'][0]
        coach = self.service.get_coach_by_id(coach_id)
        self.open_coach_dialog(coach)

    def open_coach_dialog(self, coach=None):
        """打开教练对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("教练信息" if coach else "添加教练")
        dialog.geometry("400x350")
        dialog.transient(self.parent)
        dialog.grab_set()

        y = 20
        fields = [
            ("姓名:", "name"),
            ("手机号:", "phone"),
            ("性别:", "gender"),
            ("专长:", "specialty"),
            ("月薪:", "salary"),
        ]

        entries = {}

        values = {}
        if coach:
            values = {
                'name': coach.get('name', ''),
                'phone': coach.get('phone', ''),
                'gender': coach.get('gender', '男'),
                'specialty': coach.get('specialty', ''),
                'salary': str(coach.get('salary', '')),
            }

        for label_text, field_name in fields:
            tk.Label(dialog, text=label_text).place(x=50, y=y)

            if field_name == "gender":
                var = tk.StringVar(value=values.get('gender', '男'))
                entries[field_name] = var
                tk.Radiobutton(dialog, text="男", variable=var, value="男").place(x=120, y=y)
                tk.Radiobutton(dialog, text="女", variable=var, value="女").place(x=170, y=y)
            else:
                entry = tk.Entry(dialog, width=25)
                entry.place(x=120, y=y)
                if field_name in values:
                    entry.insert(0, values[field_name])
                entries[field_name] = entry

            y += 40

        def save():
            try:
                name = entries['name'].get().strip()
                phone = entries['phone'].get().strip()
                gender = entries['gender'].get()
                specialty = entries['specialty'].get().strip() or None
                salary = float(entries['salary'].get())

                if not name or not phone:
                    messagebox.showerror("错误", "姓名和手机号不能为空")
                    return

                if coach:
                    self.service.update_coach(coach['id'], name, phone, gender, specialty, salary)
                    messagebox.showinfo("成功", "教练信息已更新")
                else:
                    self.service.add_coach(name, phone, gender, specialty, salary)
                    messagebox.showinfo("成功", "教练添加成功")

                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        tk.Button(dialog, text="保存", command=save, width=10).place(x=120, y=y+20)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=220, y=y+20)

    def delete_coach(self):
        """删除教练"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要删除的教练")
            return

        if not messagebox.askyesno("确认", "确定要删除该教练吗？"):
            return

        item = self.tree.item(selection[0])
        coach_id = item['values'][0]

        try:
            self.service.delete_coach(coach_id)
            messagebox.showinfo("成功", "教练已删除")
            self.load_data()
        except Exception as e:
            messagebox.showerror("错误", str(e))


class CourseManagerView:
    """课程管理视图"""

    def __init__(self, parent):
        self.parent = parent
        self.course_service = CourseService()
        self.schedule_service = CourseScheduleService()
        self.coach_service = CoachService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置UI"""
        tk.Label(self.parent, text="课程管理", font=("微软雅黑", 18, "bold"),
                bg="#ecf0f1").pack(pady=10)

        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 课程类别
        self.course_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(self.course_frame, text="课程类别")
        self.setup_course_tab()

        # 课程安排
        self.schedule_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(self.schedule_frame, text="课程安排")
        self.setup_schedule_tab()

    def setup_course_tab(self):
        """设置课程类别选项卡"""
        table_frame = tk.Frame(self.course_frame, bg="#ecf0f1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("编号", "名称", "类别", "时长(分钟)", "最大人数", "描述")
        self.course_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.course_tree.heading(col, text=col)
            self.course_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.course_tree.yview)
        self.course_tree.configure(yscrollcommand=scrollbar.set)

        self.course_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self.course_frame, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="添加课程", command=self.add_course, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑课程", command=self.edit_course, width=12).pack(side=tk.LEFT, padx=5)

    def setup_schedule_tab(self):
        """设置课程安排选项卡"""
        table_frame = tk.Frame(self.schedule_frame, bg="#ecf0f1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("编号", "课程名称", "教练", "时间", "教室", "最大人数", "已预约", "状态")
        self.schedule_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.schedule_tree.heading(col, text=col)

        self.schedule_tree.column("编号", width=50)
        self.schedule_tree.column("时间", width=150)
        self.schedule_tree.column("教练", width=80)
        self.schedule_tree.column("状态", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)

        self.schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self.schedule_frame, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="添加安排", command=self.add_schedule, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑安排", command=self.edit_schedule, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除安排", command=self.delete_schedule, width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        """加载数据"""
        self.load_courses()
        self.load_schedules()

    def load_courses(self):
        """加载课程数据"""
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)

        courses = self.course_service.get_all_courses()
        for c in courses:
            self.course_tree.insert("", tk.END, values=(
                c['id'], c['name'], c.get('category', ''),
                c.get('duration', ''), c.get('max_capacity', ''),
                c.get('description', '')
            ))

    def load_schedules(self):
        """加载课程安排数据"""
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)

        schedules = self.schedule_service.get_upcoming_schedules(30)
        for s in schedules:
            self.schedule_tree.insert("", tk.END, values=(
                s['id'], s['course_name'], s['coach_name'],
                s['schedule_time'], s.get('room', ''),
                s.get('max_capacity', ''), s.get('current_count', 0),
                s['status']
            ))

    def add_course(self):
        """添加课程"""
        self.open_course_dialog()

    def edit_course(self):
        """编辑课程"""
        selection = self.course_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的课程")
            return

        item = self.course_tree.item(selection[0])
        course_id = item['values'][0]
        course = self.course_service.get_course_by_id(course_id)
        self.open_course_dialog(course)

    def open_course_dialog(self, course=None):
        """打开课程对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("课程信息" if course else "添加课程")
        dialog.geometry("400x350")
        dialog.transient(self.parent)
        dialog.grab_set()

        y = 20
        fields = [
            ("名称:", "name"),
            ("类别:", "category"),
            ("时长(分钟):", "duration"),
            ("最大人数:", "max_capacity"),
            ("描述:", "description"),
        ]

        entries = {}

        values = {}
        if course:
            values = {
                'name': course.get('name', ''),
                'category': course.get('category', ''),
                'duration': str(course.get('duration', 60)),
                'max_capacity': str(course.get('max_capacity', 20)),
                'description': course.get('description', ''),
            }

        for label_text, field_name in fields:
            tk.Label(dialog, text=label_text).place(x=50, y=y)

            if field_name == "category":
                var = tk.StringVar(value=values.get('category', '瑜伽'))
                entries[field_name] = var
                for i, opt in enumerate(['瑜伽', '单车', '普拉提', '操课', '其他']):
                    tk.Radiobutton(dialog, text=opt, variable=var, value=opt).place(x=120 + i*60, y=y)
            else:
                entry = tk.Entry(dialog, width=25)
                entry.place(x=120, y=y)
                if field_name in values:
                    entry.insert(0, values[field_name])
                entries[field_name] = entry

            y += 40

        def save():
            try:
                name = entries['name'].get().strip()
                category = entries['category'].get()
                duration = int(entries['duration'].get())
                max_capacity = int(entries['max_capacity'].get())
                description = entries['description'].get().strip() or None

                if not name:
                    messagebox.showerror("错误", "课程名称不能为空")
                    return

                if course:
                    self.course_service.update_course(course['id'], name, category, duration, max_capacity, description)
                    messagebox.showinfo("成功", "课程已更新")
                else:
                    self.course_service.add_course(name, category, duration, max_capacity, description)
                    messagebox.showinfo("成功", "课程添加成功")

                dialog.destroy()
                self.load_courses()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        tk.Button(dialog, text="保存", command=save, width=10).place(x=120, y=y+20)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=220, y=y+20)

    def add_schedule(self):
        """添加课程安排"""
        self.open_schedule_dialog()

    def edit_schedule(self):
        """编辑课程安排"""
        selection = self.schedule_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的安排")
            return

        item = self.schedule_tree.item(selection[0])
        schedule_id = item['values'][0]
        schedule = self.schedule_service.get_schedule_by_id(schedule_id)
        self.open_schedule_dialog(schedule)

    def open_schedule_dialog(self, schedule=None):
        """打开课程安排对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("课程安排" if schedule else "添加安排")
        dialog.geometry("400x350")
        dialog.transient(self.parent)
        dialog.grab_set()

        y = 20

        # 课程选择
        tk.Label(dialog, text="选择课程:").place(x=50, y=y)
        courses = self.course_service.get_all_courses()
        course_names = [f"{c['id']}: {c['name']}" for c in courses]
        self.course_var = tk.StringVar()
        course_combo = ttk.Combobox(dialog, textvariable=self.course_var, values=course_names, width=25, state="readonly")
        course_combo.place(x=130, y=y)

        y += 40

        # 教练选择
        tk.Label(dialog, text="选择教练:").place(x=50, y=y)
        coaches = self.coach_service.get_all_coaches()
        coach_names = [f"{c['id']}: {c['name']}" for c in coaches]
        self.coach_var = tk.StringVar()
        coach_combo = ttk.Combobox(dialog, textvariable=self.coach_var, values=coach_names, width=25, state="readonly")
        coach_combo.place(x=130, y=y)

        y += 40

        # 时间
        tk.Label(dialog, text="上课时间:").place(x=50, y=y)
        time_entry = tk.Entry(dialog, width=25)
        time_entry.insert(0, "2026-04-17 09:00:00")
        time_entry.place(x=130, y=y)

        y += 40

        # 教室
        tk.Label(dialog, text="教室:").place(x=50, y=y)
        room_entry = tk.Entry(dialog, width=25)
        room_entry.place(x=130, y=y)

        y += 40

        # 最大人数
        tk.Label(dialog, text="最大人数:").place(x=50, y=y)
        capacity_entry = tk.Entry(dialog, width=25)
        capacity_entry.insert(0, "20")
        capacity_entry.place(x=130, y=y)

        # 预填值
        if schedule:
            for c in courses:
                if c['id'] == schedule['course_id']:
                    self.course_var.set(f"{c['id']}: {c['name']}")
                    break
            for c in coaches:
                if c['id'] == schedule['coach_id']:
                    self.coach_var.set(f"{c['id']}: {c['name']}")
                    break
            time_entry.delete(0, tk.END)
            time_entry.insert(0, str(schedule['schedule_time']))
            room_entry.insert(0, schedule.get('room', ''))
            capacity_entry.delete(0, tk.END)
            capacity_entry.insert(0, str(schedule.get('max_capacity', 20)))

        def save():
            try:
                course_str = self.course_var.get()
                coach_str = self.coach_var.get()
                schedule_time = time_entry.get().strip()
                room = room_entry.get().strip() or None
                max_capacity = int(capacity_entry.get())

                if not course_str or not coach_str or not schedule_time:
                    messagebox.showerror("错误", "请填写所有必填项")
                    return

                course_id = int(course_str.split(':')[0])
                coach_id = int(coach_str.split(':')[0])

                if schedule:
                    self.schedule_service.update_schedule(schedule['id'], course_id, coach_id, schedule_time, room, max_capacity)
                    messagebox.showinfo("成功", "安排已更新")
                else:
                    self.schedule_service.add_schedule(course_id, coach_id, schedule_time, room, max_capacity)
                    messagebox.showinfo("成功", "安排添加成功")

                dialog.destroy()
                self.load_schedules()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        tk.Button(dialog, text="保存", command=save, width=10).place(x=120, y=y+30)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=220, y=y+30)

    def delete_schedule(self):
        """删除课程安排"""
        selection = self.schedule_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要删除的安排")
            return

        if not messagebox.askyesno("确认", "确定要删除该安排吗？"):
            return

        item = self.schedule_tree.item(selection[0])
        schedule_id = item['values'][0]

        try:
            self.schedule_service.delete_schedule(schedule_id)
            messagebox.showinfo("成功", "安排已删除")
            self.load_schedules()
        except Exception as e:
            messagebox.showerror("错误", str(e))


class BookingManagerView:
    """预约签到视图"""

    def __init__(self, parent):
        self.parent = parent
        self.member_service = MemberService()
        self.booking_service = BookingService()
        self.schedule_service = CourseScheduleService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置UI"""
        tk.Label(self.parent, text="预约签到管理", font=("微软雅黑", 18, "bold"),
                bg="#ecf0f1").pack(pady=10)

        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 预约管理
        self.booking_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(self.booking_frame, text="预约管理")
        self.setup_booking_tab()

        # 签到管理
        self.checkin_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(self.checkin_frame, text="签到管理")
        self.setup_checkin_tab()

    def setup_booking_tab(self):
        """设置预约选项卡"""
        table_frame = tk.Frame(self.booking_frame, bg="#ecf0f1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("编号", "会员姓名", "会员手机", "课程", "上课时间", "预约时间", "状态")
        self.booking_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.booking_tree.heading(col, text=col)
            self.booking_tree.column(col, width=120)

        self.booking_tree.column("编号", width=50)
        self.booking_tree.column("状态", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.booking_tree.yview)
        self.booking_tree.configure(yscrollcommand=scrollbar.set)

        self.booking_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self.booking_frame, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="课程预约", command=self.open_booking_dialog, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消预约", command=self.cancel_booking, width=12).pack(side=tk.LEFT, padx=5)

    def setup_checkin_tab(self):
        """设置签到选项卡"""
        table_frame = tk.Frame(self.checkin_frame, bg="#ecf0f1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("编号", "会员姓名", "会员手机", "课程", "上课时间", "预约时间", "签到时间", "状态")
        self.checkin_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.checkin_tree.heading(col, text=col)
            self.checkin_tree.column(col, width=110)

        self.checkin_tree.column("编号", width=50)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.checkin_tree.yview)
        self.checkin_tree.configure(yscrollcommand=scrollbar.set)

        self.checkin_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self.checkin_frame, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="会员签到", command=self.checkin, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="课程评价", command=self.open_rating_dialog, width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        """加载数据"""
        self.load_bookings()
        self.load_checkins()

    def load_bookings(self):
        """加载预约数据"""
        for item in self.booking_tree.get_children():
            self.booking_tree.delete(item)

        bookings = self.booking_service.get_all_bookings()
        for b in bookings:
            self.booking_tree.insert("", tk.END, values=(
                b['id'], b['member_name'], b['member_phone'],
                b['course_name'], b['schedule_time'],
                b['book_time'], b['status']
            ))

    def load_checkins(self):
        """加载签到数据"""
        for item in self.checkin_tree.get_children():
            self.checkin_tree.delete(item)

        bookings = self.booking_service.get_all_bookings()
        for b in bookings:
            checkin_time = b.get('checkin_time', '') or ''
            self.checkin_tree.insert("", tk.END, values=(
                b['id'], b['member_name'], b['member_phone'],
                b['course_name'], b['schedule_time'],
                b['book_time'], checkin_time, b['status']
            ))

    def open_booking_dialog(self):
        """打开预约对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("课程预约")
        dialog.geometry("400x250")
        dialog.transient(self.parent)
        dialog.grab_set()

        y = 30

        # 会员选择
        tk.Label(dialog, text="选择会员:").place(x=50, y=y)
        members = self.member_service.get_all_members()
        member_names = [f"{m['id']}: {m['name']} ({m['phone']})" for m in members]
        self.book_member_var = tk.StringVar()
        member_combo = ttk.Combobox(dialog, textvariable=self.book_member_var, values=member_names, width=25, state="readonly")
        member_combo.place(x=130, y=y)

        y += 50

        # 课程安排选择
        tk.Label(dialog, text="选择课程:").place(x=50, y=y)
        schedules = self.schedule_service.get_upcoming_schedules(30)
        schedule_info = [f"{s['id']}: {s['course_name']} - {s['coach_name']} ({s['schedule_time']})" for s in schedules]
        self.book_schedule_var = tk.StringVar()
        schedule_combo = ttk.Combobox(dialog, textvariable=self.book_schedule_var, values=schedule_info, width=25, state="readonly")
        schedule_combo.place(x=130, y=y)

        def save():
            try:
                member_str = self.book_member_var.get()
                schedule_str = self.book_schedule_var.get()

                if not member_str or not schedule_str:
                    messagebox.showerror("错误", "请选择会员和课程")
                    return

                member_id = int(member_str.split(':')[0])
                schedule_id = int(schedule_str.split(':')[0])

                self.booking_service.book_course(member_id, schedule_id)
                messagebox.showinfo("成功", "预约成功")
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        tk.Button(dialog, text="预约", command=save, width=10).place(x=120, y=y+50)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=220, y=y+50)

    def cancel_booking(self):
        """取消预约"""
        selection = self.booking_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要取消的预约")
            return

        if not messagebox.askyesno("确认", "确定要取消该预约吗？"):
            return

        item = self.booking_tree.item(selection[0])
        booking_id = item['values'][0]

        try:
            self.booking_service.cancel_booking(booking_id)
            messagebox.showinfo("成功", "预约已取消")
            self.load_data()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def checkin(self):
        """签到"""
        selection = self.checkin_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要签到的会员")
            return

        item = self.checkin_tree.item(selection[0])
        booking_id = item['values'][0]
        status = item['values'][6]

        if status != '已预约':
            messagebox.showwarning("提示", "该预约已签到或已取消")
            return

        try:
            self.booking_service.checkin_booking(booking_id)
            messagebox.showinfo("成功", "签到成功！\n系统已自动扣减会员卡次数/有效期")
            self.load_data()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def open_rating_dialog(self):
        """打开评价对话框"""
        selection = self.checkin_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要评价的预约")
            return

        item = self.checkin_tree.item(selection[0])
        booking_id = item['values'][0]

        dialog = tk.Toplevel(self.parent)
        dialog.title("课程评价")
        dialog.geometry("300x200")
        dialog.transient(self.parent)
        dialog.grab_set()

        tk.Label(dialog, text="请选择评分:").pack(pady=20)

        self.rating_var = tk.IntVar(value=5)
        for i in range(1, 6):
            tk.Radiobutton(dialog, text=f"{i}星", variable=self.rating_var, value=i).pack()

        tk.Label(dialog, text="评价备注:").pack(pady=10)
        remark_entry = tk.Entry(dialog, width=30)
        remark_entry.pack()

        def save():
            try:
                rating = self.rating_var.get()
                remark = remark_entry.get().strip() or None
                self.booking_service.rate_booking(booking_id, rating, remark)
                messagebox.showinfo("成功", "评价已提交")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        tk.Button(dialog, text="提交", command=save, width=10).pack(pady=20)


class EquipmentManagerView:
    """器材管理视图"""

    def __init__(self, parent):
        self.parent = parent
        self.equipment_service = EquipmentService()
        self.borrow_service = EquipmentBorrowService()
        self.member_service = MemberService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置UI"""
        tk.Label(self.parent, text="器材管理", font=("微软雅黑", 18, "bold"),
                bg="#ecf0f1").pack(pady=10)

        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 器材管理
        self.equip_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(self.equip_frame, text="器材信息")
        self.setup_equipment_tab()

        # 借用管理
        self.borrow_frame = tk.Frame(notebook, bg="#ecf0f1")
        notebook.add(self.borrow_frame, text="借用管理")
        self.setup_borrow_tab()

    def setup_equipment_tab(self):
        """设置器材选项卡"""
        table_frame = tk.Frame(self.equip_frame, bg="#ecf0f1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("编号", "名称", "类别", "状态", "购买日期", "备注")
        self.equip_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.equip_tree.heading(col, text=col)
            self.equip_tree.column(col, width=120)

        self.equip_tree.column("编号", width=50)
        self.equip_tree.column("状态", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.equip_tree.yview)
        self.equip_tree.configure(yscrollcommand=scrollbar.set)

        self.equip_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self.equip_frame, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="添加器材", command=self.add_equipment, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑器材", command=self.edit_equipment, width=12).pack(side=tk.LEFT, padx=5)

    def setup_borrow_tab(self):
        """设置借用选项卡"""
        table_frame = tk.Frame(self.borrow_frame, bg="#ecf0f1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("编号", "器材名称", "器材类别", "会员姓名", "会员手机", "借用时间", "状态")
        self.borrow_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.borrow_tree.heading(col, text=col)
            self.borrow_tree.column(col, width=120)

        self.borrow_tree.column("编号", width=50)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.borrow_tree.yview)
        self.borrow_tree.configure(yscrollcommand=scrollbar.set)

        self.borrow_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self.borrow_frame, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="借用器材", command=self.borrow_equipment, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="归还器材", command=self.return_equipment, width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        """加载数据"""
        self.load_equipment()
        self.load_borrow_records()

    def load_equipment(self):
        """加载器材数据"""
        for item in self.equip_tree.get_children():
            self.equip_tree.delete(item)

        equipment = self.equipment_service.get_all_equipment()
        for e in equipment:
            buy_date = e.get('buy_date', '') or ''
            self.equip_tree.insert("", tk.END, values=(
                e['id'], e['name'], e.get('equipment_type', ''),
                e['status'], buy_date, e.get('remark', '')
            ))

    def load_borrow_records(self):
        """加载借用记录"""
        for item in self.borrow_tree.get_children():
            self.borrow_tree.delete(item)

        records = self.borrow_service.get_all_borrow_records()
        for r in records:
            self.borrow_tree.insert("", tk.END, values=(
                r['id'], r['equipment_name'], r['equipment_type'],
                r['member_name'], r['member_phone'],
                r['borrow_time'], r['status']
            ))

    def add_equipment(self):
        """添加器材"""
        self.open_equipment_dialog()

    def edit_equipment(self):
        """编辑器材"""
        selection = self.equip_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的器材")
            return

        item = self.equip_tree.item(selection[0])
        equipment_id = item['values'][0]
        equipment = self.equipment_service.get_equipment_by_id(equipment_id)
        self.open_equipment_dialog(equipment)

    def open_equipment_dialog(self, equipment=None):
        """打开器材对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("器材信息" if equipment else "添加器材")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()

        y = 20
        fields = [
            ("名称:", "name"),
            ("类别:", "equipment_type"),
            ("备注:", "remark"),
        ]

        entries = {}

        values = {}
        if equipment:
            values = {
                'name': equipment.get('name', ''),
                'equipment_type': equipment.get('equipment_type', ''),
                'remark': equipment.get('remark', ''),
            }

        for label_text, field_name in fields:
            tk.Label(dialog, text=label_text).place(x=50, y=y)
            entry = tk.Entry(dialog, width=25)
            entry.place(x=120, y=y)
            if field_name in values:
                entry.insert(0, values[field_name])
            entries[field_name] = entry
            y += 40

        def save():
            try:
                name = entries['name'].get().strip()
                equipment_type = entries['equipment_type'].get().strip() or None
                remark = entries['remark'].get().strip() or None

                if not name:
                    messagebox.showerror("错误", "器材名称不能为空")
                    return

                if equipment:
                    self.equipment_service.update_equipment(equipment['id'], name, equipment_type, remark)
                    messagebox.showinfo("成功", "器材已更新")
                else:
                    self.equipment_service.add_equipment(name, equipment_type, None, remark)
                    messagebox.showinfo("成功", "器材添加成功")

                dialog.destroy()
                self.load_equipment()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        tk.Button(dialog, text="保存", command=save, width=10).place(x=120, y=y+20)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=220, y=y+20)

    def borrow_equipment(self):
        """借用器材"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("借用器材")
        dialog.geometry("400x200")
        dialog.transient(self.parent)
        dialog.grab_set()

        y = 30

        tk.Label(dialog, text="选择会员:").place(x=50, y=y)
        members = self.member_service.get_all_members()
        member_names = [f"{m['id']}: {m['name']} ({m['phone']})" for m in members]
        self.borrow_member_var = tk.StringVar()
        member_combo = ttk.Combobox(dialog, textvariable=self.borrow_member_var, values=member_names, width=25, state="readonly")
        member_combo.place(x=130, y=y)

        y += 50

        tk.Label(dialog, text="选择器材:").place(x=50, y=y)
        available = self.equipment_service.get_available_equipment()
        equip_names = [f"{e['id']}: {e['name']} ({e['equipment_type']})" for e in available]
        self.borrow_equip_var = tk.StringVar()
        equip_combo = ttk.Combobox(dialog, textvariable=self.borrow_equip_var, values=equip_names, width=25, state="readonly")
        equip_combo.place(x=130, y=y)

        def save():
            try:
                member_str = self.borrow_member_var.get()
                equip_str = self.borrow_equip_var.get()

                if not member_str or not equip_str:
                    messagebox.showerror("错误", "请选择会员和器材")
                    return

                member_id = int(member_str.split(':')[0])
                equipment_id = int(equip_str.split(':')[0])

                self.borrow_service.borrow_equipment(equipment_id, member_id)
                messagebox.showinfo("成功", "借用成功")
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        tk.Button(dialog, text="借用", command=save, width=10).place(x=120, y=y+50)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=220, y=y+50)

    def return_equipment(self):
        """归还器材"""
        selection = self.borrow_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要归还的记录")
            return

        item = self.borrow_tree.item(selection[0])
        record_id = item['values'][0]
        status = item['values'][6]

        if status == '已归还':
            messagebox.showwarning("提示", "该器材已归还")
            return

        if not messagebox.askyesno("确认", "确定要归还该器材吗？"):
            return

        try:
            self.borrow_service.return_equipment(record_id)
            messagebox.showinfo("成功", "归还成功")
            self.load_data()
        except Exception as e:
            messagebox.showerror("错误", str(e))


class ReportViewer:
    """数据报表视图"""

    def __init__(self, parent):
        self.parent = parent
        self.stats_service = WeeklyStatsService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置UI"""
        tk.Label(self.parent, text="课程预约统计报表", font=("微软雅黑", 18, "bold"),
                bg="#ecf0f1").pack(pady=10)

        tk.Label(self.parent, text="近一周各课程预约人数、签到人数及签到率",
                font=("微软雅黑", 10), bg="#ecf0f1", fg="#7f8c8d").pack()

        # 表格
        table_frame = tk.Frame(self.parent, bg="#ecf0f1")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        columns = ("课程ID", "课程名称", "类别", "安排次数", "预约人数", "签到人数", "签到率(%)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.column("课程ID", width=70)
        self.tree.column("课程名称", width=120)
        self.tree.column("签到率(%)", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 刷新按钮
        btn_frame = tk.Frame(self.parent, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="刷新数据", command=self.load_data, width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        """加载数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            stats = self.stats_service.get_weekly_stats()
            for s in stats:
                rate = s.get('checkin_rate', 0) or 0
                self.tree.insert("", tk.END, values=(
                    s['course_id'], s['course_name'], s['course_category'],
                    s.get('total_schedules', 0), s.get('booking_count', 0),
                    s.get('checkin_count', 0), f"{rate}%"
                ))
        except Exception as e:
            messagebox.showerror("错误", f"加载数据失败: {e}")


class ConsumptionQueryView:
    """消费查询视图"""

    def __init__(self, parent):
        self.parent = parent
        self.member_service = MemberService()
        self.card_service = MemberCardService()
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        tk.Label(self.parent, text="会员消费查询", font=("微软雅黑", 18, "bold"),
                bg="#ecf0f1").pack(pady=10)

        # 选择会员
        select_frame = tk.Frame(self.parent, bg="#ecf0f1")
        select_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(select_frame, text="选择会员:", bg="#ecf0f1").pack(side=tk.LEFT)
        members = self.member_service.get_all_members()
        member_names = [f"{m['id']}: {m['name']} ({m['phone']})" for m in members]
        self.member_var = tk.StringVar()
        member_combo = ttk.Combobox(select_frame, textvariable=self.member_var,
                                   values=member_names, width=30, state="readonly")
        member_combo.pack(side=tk.LEFT, padx=10)
        member_combo.bind("<<ComboboxSelected>>", lambda e: self.query())

        tk.Button(select_frame, text="查询", command=self.query, width=10).pack(side=tk.LEFT, padx=10)

        # 结果显示区
        self.result_frame = tk.Frame(self.parent, bg="#ecf0f1")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 文本框显示结果
        self.result_text = tk.Text(self.result_frame, width=80, height=20,
                                   font=("微软雅黑", 10), bg="white")
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(self.result_text, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)

    def query(self):
        """查询消费明细"""
        member_str = self.member_var.get()
        if not member_str:
            return

        member_id = int(member_str.split(':')[0])

        self.result_text.delete(1.0, tk.END)

        try:
            results = self.card_service.get_member_consumption(member_id)

            if not results:
                self.result_text.insert(tk.END, "未找到该会员的消费记录\n")
                return

            current_type = None
            for row in results:
                info_type = row.get('info_type', '')
                info_detail = row.get('info_detail', '')
                info_value = row.get('info_value', '')

                if info_type != current_type:
                    self.result_text.insert(tk.END, f"\n{'='*40}\n")
                    self.result_text.insert(tk.END, f"【{info_type}】\n")
                    self.result_text.insert(tk.END, f"{'='*40}\n")
                    current_type = info_type

                self.result_text.insert(tk.END, f"  {info_detail}: {info_value}\n")

        except Exception as e:
            self.result_text.insert(tk.END, f"查询失败: {e}\n")


def run():
    """运行主程序"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    run()
