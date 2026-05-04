import tkinter as tk
from tkinter import messagebox, ttk

from services.member_service import CardTypeService, MemberCardService, MemberService
from views.common import WINDOW_BG, clear_tree, create_action_bar, create_section_title, create_table


class MemberManagerView:
    """会员管理视图。"""

    def __init__(self, parent):
        self.parent = parent
        self.service = MemberService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        create_section_title(self.parent, "会员管理")

        search_frame = tk.Frame(self.parent, bg=WINDOW_BG)
        search_frame.pack(fill=tk.X, padx=20)

        tk.Label(search_frame, text="搜索:", bg=WINDOW_BG).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="查询", command=self.search, width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="显示全部", command=self.load_data, width=8).pack(side=tk.LEFT)

        columns = ("编号", "姓名", "手机号", "性别", "身份证号", "入会日期", "状态", "备注")
        widths = {"编号": 60, "姓名": 90, "手机号": 120, "身份证号": 160, "备注": 180}
        self.tree = create_table(self.parent, columns, widths, height=15)

        btn_frame = create_action_bar(self.parent)
        tk.Button(btn_frame, text="添加会员", command=self.add_member, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑会员", command=self.edit_member, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除会员", command=self.delete_member, width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        clear_tree(self.tree)
        for member in self.service.get_all_members():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    member["id"],
                    member["name"],
                    member["phone"],
                    member["gender"],
                    member.get("id_card", "") or "",
                    member["join_date"],
                    member["status"],
                    member.get("remark", "") or "",
                ),
            )

    def search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_data()
            return

        clear_tree(self.tree)
        for member in self.service.search_member(keyword):
            self.tree.insert(
                "",
                tk.END,
                values=(
                    member["id"],
                    member["name"],
                    member["phone"],
                    member["gender"],
                    member.get("id_card", "") or "",
                    member["join_date"],
                    member["status"],
                    member.get("remark", "") or "",
                ),
            )

    def add_member(self):
        self.open_member_dialog()

    def edit_member(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的会员")
            return
        member_id = self.tree.item(selection[0])["values"][0]
        self.open_member_dialog(self.service.get_member_by_id(member_id))

    def open_member_dialog(self, member=None):
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑会员" if member else "添加会员")
        dialog.geometry("420x360")
        dialog.transient(self.parent)
        dialog.grab_set()

        values = member or {}
        labels = [
            ("姓名", "name"),
            ("手机号", "phone"),
            ("身份证号", "id_card"),
            ("备注", "remark"),
        ]

        entries = {}
        y = 20
        for text, key in labels:
            tk.Label(dialog, text=f"{text}:").place(x=50, y=y)
            entry = tk.Entry(dialog, width=28)
            entry.place(x=130, y=y)
            entry.insert(0, values.get(key, "") or "")
            entries[key] = entry
            y += 40

        tk.Label(dialog, text="性别:").place(x=50, y=y)
        gender_var = tk.StringVar(value=values.get("gender", "男"))
        tk.Radiobutton(dialog, text="男", variable=gender_var, value="男").place(x=130, y=y)
        tk.Radiobutton(dialog, text="女", variable=gender_var, value="女").place(x=190, y=y)
        y += 40

        tk.Label(dialog, text="状态:").place(x=50, y=y)
        status_var = tk.StringVar(value=values.get("status", "正常"))
        for index, option in enumerate(["正常", "冻结", "已过期"]):
            tk.Radiobutton(dialog, text=option, variable=status_var, value=option).place(x=130 + index * 70, y=y)

        def save():
            try:
                name = entries["name"].get().strip()
                phone = entries["phone"].get().strip()
                if not name or not phone:
                    raise ValueError("姓名和手机号不能为空")

                payload = {
                    "name": name,
                    "phone": phone,
                    "gender": gender_var.get(),
                    "id_card": entries["id_card"].get().strip() or None,
                    "remark": entries["remark"].get().strip() or None,
                    "status": status_var.get(),
                }
                if member:
                    self.service.update_member(member["id"], **payload)
                else:
                    self.service.add_member(
                        payload["name"],
                        payload["phone"],
                        payload["gender"],
                        payload["id_card"],
                        payload["remark"],
                    )
                dialog.destroy()
                self.load_data()
                messagebox.showinfo("成功", "会员信息已保存")
            except Exception as exc:
                messagebox.showerror("错误", str(exc))

        tk.Button(dialog, text="保存", command=save, width=10).place(x=130, y=y + 50)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=240, y=y + 50)

    def delete_member(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要删除的会员")
            return
        if not messagebox.askyesno("确认", "确定删除该会员吗？"):
            return

        member_id = self.tree.item(selection[0])["values"][0]
        try:
            self.service.delete_member(member_id)
            self.load_data()
            messagebox.showinfo("成功", "会员已删除")
        except Exception as exc:
            messagebox.showerror("错误", str(exc))


class CardManagerView:
    """会员卡管理视图。"""

    def __init__(self, parent):
        self.parent = parent
        self.member_service = MemberService()
        self.card_type_service = CardTypeService()
        self.member_card_service = MemberCardService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        create_section_title(self.parent, "会员卡管理")

        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.card_type_frame = tk.Frame(notebook, bg=WINDOW_BG)
        self.member_card_frame = tk.Frame(notebook, bg=WINDOW_BG)
        notebook.add(self.card_type_frame, text="卡类型")
        notebook.add(self.member_card_frame, text="办卡记录")

        self.setup_card_type_tab()
        self.setup_member_card_tab()

    def setup_card_type_tab(self):
        columns = ("编号", "名称", "类别", "限制次数", "有效期天数", "价格", "描述")
        widths = {"编号": 60, "名称": 120, "价格": 90, "描述": 220}
        self.card_type_tree = create_table(self.card_type_frame, columns, widths)
        btn_frame = create_action_bar(self.card_type_frame)
        tk.Button(btn_frame, text="添加卡类型", command=self.add_card_type, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑卡类型", command=self.edit_card_type, width=12).pack(side=tk.LEFT, padx=5)

    def setup_member_card_tab(self):
        columns = ("编号", "会员姓名", "手机号", "卡类型", "购卡日期", "有效期至", "剩余次数", "状态", "价格")
        widths = {"编号": 60, "会员姓名": 90, "手机号": 120, "有效期至": 110, "剩余次数": 90, "价格": 90}
        self.member_card_tree = create_table(self.member_card_frame, columns, widths)
        btn_frame = create_action_bar(self.member_card_frame)
        tk.Button(btn_frame, text="办理新卡", command=self.open_buy_card_dialog, width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        self.load_card_types()
        self.load_member_cards()

    def load_card_types(self):
        clear_tree(self.card_type_tree)
        for card_type in self.card_type_service.get_all_card_types():
            self.card_type_tree.insert(
                "",
                tk.END,
                values=(
                    card_type["id"],
                    card_type["name"],
                    card_type["card_category"],
                    card_type.get("times_limit", "") or "",
                    card_type.get("valid_days", "") or "",
                    card_type["price"],
                    card_type.get("description", "") or "",
                ),
            )

    def load_member_cards(self):
        clear_tree(self.member_card_tree)
        for card in self.member_card_service.get_all_member_cards():
            self.member_card_tree.insert(
                "",
                tk.END,
                values=(
                    card["id"],
                    card["member_name"],
                    card["member_phone"],
                    card["card_type_name"],
                    card["buy_date"],
                    card.get("expire_date", "") or "",
                    card.get("remain_times", "") or "",
                    card["status"],
                    card["price"],
                ),
            )

    def add_card_type(self):
        self.open_card_type_dialog()

    def edit_card_type(self):
        selection = self.card_type_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的卡类型")
            return
        card_type_id = self.card_type_tree.item(selection[0])["values"][0]
        self.open_card_type_dialog(self.card_type_service.get_card_type_by_id(card_type_id))

    def open_card_type_dialog(self, card_type=None):
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑卡类型" if card_type else "添加卡类型")
        dialog.geometry("440x340")
        dialog.transient(self.parent)
        dialog.grab_set()

        values = card_type or {}
        y = 20

        tk.Label(dialog, text="名称:").place(x=50, y=y)
        name_entry = tk.Entry(dialog, width=28)
        name_entry.place(x=140, y=y)
        name_entry.insert(0, values.get("name", "") or "")
        y += 40

        tk.Label(dialog, text="卡类别:").place(x=50, y=y)
        category_var = tk.StringVar(value=values.get("card_category", "月卡"))
        options = self.card_type_service.get_card_type_options()
        for index, option in enumerate(options):
            tk.Radiobutton(dialog, text=option["label"], variable=category_var, value=option["label"]).place(
                x=140 + index * 65, y=y
            )
        y += 40

        tk.Label(dialog, text="限制次数:").place(x=50, y=y)
        times_entry = tk.Entry(dialog, width=28)
        times_entry.place(x=140, y=y)
        times_entry.insert(0, str(values.get("times_limit", "") or ""))
        y += 40

        tk.Label(dialog, text="有效期天数:").place(x=50, y=y)
        valid_days_entry = tk.Entry(dialog, width=28)
        valid_days_entry.place(x=140, y=y)
        valid_days_entry.insert(0, str(values.get("valid_days", "") or ""))
        y += 40

        tk.Label(dialog, text="价格:").place(x=50, y=y)
        price_entry = tk.Entry(dialog, width=28)
        price_entry.place(x=140, y=y)
        price_entry.insert(0, str(values.get("price", "") or ""))
        y += 40

        tk.Label(dialog, text="描述:").place(x=50, y=y)
        desc_entry = tk.Entry(dialog, width=28)
        desc_entry.place(x=140, y=y)
        desc_entry.insert(0, values.get("description", "") or "")

        def save():
            try:
                name = name_entry.get().strip()
                category = category_var.get()
                price = float(price_entry.get().strip())
                times_limit = times_entry.get().strip()
                valid_days = valid_days_entry.get().strip()
                description = desc_entry.get().strip() or None

                if not name:
                    raise ValueError("卡类型名称不能为空")

                times_limit_value = int(times_limit) if times_limit else None
                valid_days_value = int(valid_days) if valid_days else None
                if category == "次卡" and not times_limit_value:
                    raise ValueError("次卡必须设置限制次数")
                if category != "次卡" and not valid_days_value:
                    raise ValueError("时限卡必须设置有效期天数")

                if card_type:
                    self.card_type_service.update_card_type(
                        card_type["id"], name, category, times_limit_value, valid_days_value, price, description
                    )
                else:
                    self.card_type_service.add_card_type(
                        name, category, times_limit_value, valid_days_value, price, description
                    )
                dialog.destroy()
                self.load_card_types()
                messagebox.showinfo("成功", "卡类型已保存")
            except Exception as exc:
                messagebox.showerror("错误", str(exc))

        tk.Button(dialog, text="保存", command=save, width=10).place(x=140, y=y + 50)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=250, y=y + 50)

    def open_buy_card_dialog(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("办理会员卡")
        dialog.geometry("430x260")
        dialog.transient(self.parent)
        dialog.grab_set()

        tk.Label(dialog, text="选择会员:").place(x=50, y=40)
        members = self.member_service.get_all_members()
        member_values = [f"{item['id']}: {item['name']} ({item['phone']})" for item in members]
        member_var = tk.StringVar()
        ttk.Combobox(dialog, textvariable=member_var, values=member_values, state="readonly", width=28).place(x=140, y=40)

        tk.Label(dialog, text="选择卡类型:").place(x=50, y=90)
        card_types = self.card_type_service.get_all_card_types()
        card_values = [f"{item['id']}: {item['name']} (¥{item['price']})" for item in card_types]
        card_var = tk.StringVar()
        ttk.Combobox(dialog, textvariable=card_var, values=card_values, state="readonly", width=28).place(x=140, y=90)

        tk.Label(dialog, text="购卡说明:").place(x=50, y=140)
        tip_label = tk.Label(dialog, text="系统将自动写入购卡日期、有效期或剩余次数", bg=WINDOW_BG, fg="#7f8c8d")
        tip_label.place(x=140, y=140)

        def save():
            try:
                if not member_var.get() or not card_var.get():
                    raise ValueError("请选择会员和卡类型")
                member_id = int(member_var.get().split(":")[0])
                card_type_id = int(card_var.get().split(":")[0])
                card_type = self.card_type_service.get_card_type_by_id(card_type_id)
                self.member_card_service.add_member_card(member_id, card_type_id, card_type["price"])
                dialog.destroy()
                self.load_member_cards()
                messagebox.showinfo("成功", "会员卡办理成功")
            except Exception as exc:
                messagebox.showerror("错误", str(exc))

        tk.Button(dialog, text="办理", command=save, width=10).place(x=140, y=190)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=250, y=190)
