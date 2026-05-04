import tkinter as tk
from tkinter import messagebox, ttk

from services.equipment_service import EquipmentBorrowService, EquipmentService
from services.member_service import MemberService
from views.common import WINDOW_BG, clear_tree, create_action_bar, create_section_title, create_table


class EquipmentManagerView:
    """器材管理与借还视图。"""

    def __init__(self, parent):
        self.parent = parent
        self.equipment_service = EquipmentService()
        self.borrow_service = EquipmentBorrowService()
        self.member_service = MemberService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        create_section_title(self.parent, "器材管理")

        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.equipment_frame = tk.Frame(notebook, bg=WINDOW_BG)
        self.borrow_frame = tk.Frame(notebook, bg=WINDOW_BG)
        notebook.add(self.equipment_frame, text="器材信息")
        notebook.add(self.borrow_frame, text="借还记录")

        self.setup_equipment_tab()
        self.setup_borrow_tab()

    def setup_equipment_tab(self):
        columns = ("编号", "名称", "类别", "状态", "购入日期", "备注")
        widths = {"编号": 60, "名称": 120, "类别": 120, "状态": 80, "备注": 220}
        self.equipment_tree = create_table(self.equipment_frame, columns, widths)
        btn_frame = create_action_bar(self.equipment_frame)
        tk.Button(btn_frame, text="添加器材", command=self.add_equipment, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑器材", command=self.edit_equipment, width=12).pack(side=tk.LEFT, padx=5)

    def setup_borrow_tab(self):
        columns = ("编号", "器材名称", "类别", "会员姓名", "手机号", "借用时间", "归还时间", "状态")
        widths = {"编号": 60, "器材名称": 120, "类别": 100, "会员姓名": 90, "手机号": 120, "借用时间": 160, "归还时间": 160}
        self.borrow_tree = create_table(self.borrow_frame, columns, widths)
        btn_frame = create_action_bar(self.borrow_frame)
        tk.Button(btn_frame, text="借用器材", command=self.borrow_equipment, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="归还器材", command=self.return_equipment, width=12).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        self.load_equipment()
        self.load_borrow_records()

    def load_equipment(self):
        clear_tree(self.equipment_tree)
        for equipment in self.equipment_service.get_all_equipment():
            self.equipment_tree.insert(
                "",
                tk.END,
                values=(
                    equipment["id"],
                    equipment["name"],
                    equipment.get("equipment_type", "") or "",
                    equipment["status"],
                    equipment.get("buy_date", "") or "",
                    equipment.get("remark", "") or "",
                ),
            )

    def load_borrow_records(self):
        clear_tree(self.borrow_tree)
        for record in self.borrow_service.get_all_borrow_records():
            self.borrow_tree.insert(
                "",
                tk.END,
                values=(
                    record["id"],
                    record["equipment_name"],
                    record.get("equipment_type", "") or "",
                    record["member_name"],
                    record["member_phone"],
                    record["borrow_time"],
                    record.get("return_time", "") or "",
                    record["status"],
                ),
            )

    def add_equipment(self):
        self.open_equipment_dialog()

    def edit_equipment(self):
        selection = self.equipment_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要编辑的器材")
            return
        equipment_id = self.equipment_tree.item(selection[0])["values"][0]
        self.open_equipment_dialog(self.equipment_service.get_equipment_by_id(equipment_id))

    def open_equipment_dialog(self, equipment=None):
        dialog = tk.Toplevel(self.parent)
        dialog.title("编辑器材" if equipment else "添加器材")
        dialog.geometry("420x260")
        dialog.transient(self.parent)
        dialog.grab_set()

        values = equipment or {}
        entries = {}
        y = 20
        for text, key in [("名称", "name"), ("类别", "equipment_type"), ("备注", "remark")]:
            tk.Label(dialog, text=f"{text}:").place(x=50, y=y)
            entry = tk.Entry(dialog, width=28)
            entry.place(x=130, y=y)
            entry.insert(0, values.get(key, "") or "")
            entries[key] = entry
            y += 40

        def save():
            try:
                name = entries["name"].get().strip()
                if not name:
                    raise ValueError("器材名称不能为空")
                equipment_type = entries["equipment_type"].get().strip() or None
                remark = entries["remark"].get().strip() or None
                if equipment:
                    self.equipment_service.update_equipment(equipment["id"], name, equipment_type, remark)
                else:
                    self.equipment_service.add_equipment(name, equipment_type, None, remark)
                dialog.destroy()
                self.load_equipment()
                messagebox.showinfo("成功", "器材信息已保存")
            except Exception as exc:
                messagebox.showerror("错误", str(exc))

        tk.Button(dialog, text="保存", command=save, width=10).place(x=130, y=y + 20)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=240, y=y + 20)

    def borrow_equipment(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("借用器材")
        dialog.geometry("450x220")
        dialog.transient(self.parent)
        dialog.grab_set()

        members = self.member_service.get_all_members()
        equipment = self.equipment_service.get_available_equipment()
        member_var = tk.StringVar()
        equipment_var = tk.StringVar()

        tk.Label(dialog, text="选择会员:").place(x=50, y=50)
        ttk.Combobox(
            dialog,
            textvariable=member_var,
            values=[f"{item['id']}: {item['name']} ({item['phone']})" for item in members],
            state="readonly",
            width=30,
        ).place(x=140, y=50)

        tk.Label(dialog, text="选择器材:").place(x=50, y=100)
        ttk.Combobox(
            dialog,
            textvariable=equipment_var,
            values=[f"{item['id']}: {item['name']} ({item.get('equipment_type', '') or '未分类'})" for item in equipment],
            state="readonly",
            width=30,
        ).place(x=140, y=100)

        def save():
            try:
                if not member_var.get() or not equipment_var.get():
                    raise ValueError("请选择会员和器材")
                member_id = int(member_var.get().split(":")[0])
                equipment_id = int(equipment_var.get().split(":")[0])
                self.borrow_service.borrow_equipment(equipment_id, member_id)
                dialog.destroy()
                self.load_data()
                messagebox.showinfo("成功", "器材借用成功")
            except Exception as exc:
                messagebox.showerror("错误", str(exc))

        tk.Button(dialog, text="借用", command=save, width=10).place(x=140, y=160)
        tk.Button(dialog, text="取消", command=dialog.destroy, width=10).place(x=250, y=160)

    def return_equipment(self):
        selection = self.borrow_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要归还的借用记录")
            return
        values = self.borrow_tree.item(selection[0])["values"]
        record_id = values[0]
        status = values[7]
        if status != "借用中":
            messagebox.showwarning("提示", "该记录已经归还")
            return
        try:
            self.borrow_service.return_equipment(record_id)
            self.load_data()
            messagebox.showinfo("成功", "器材已归还")
        except Exception as exc:
            messagebox.showerror("错误", str(exc))
