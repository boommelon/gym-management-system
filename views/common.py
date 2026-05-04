import tkinter as tk
from tkinter import ttk


WINDOW_BG = "#ecf0f1"
TITLE_FONT = ("Microsoft YaHei UI", 18, "bold")
TEXT_FONT = ("Microsoft YaHei UI", 10)


def clear_tree(tree):
    for item in tree.get_children():
        tree.delete(item)


def create_section_title(parent, text):
    label = tk.Label(parent, text=text, font=TITLE_FONT, bg=WINDOW_BG, fg="#2c3e50")
    label.pack(pady=10)
    return label


def create_table(parent, columns, widths=None, height=12):
    frame = tk.Frame(parent, bg=WINDOW_BG)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
    widths = widths or {}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=widths.get(col, 120), anchor=tk.CENTER)

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    return tree


def create_action_bar(parent):
    frame = tk.Frame(parent, bg=WINDOW_BG)
    frame.pack(fill=tk.X, padx=20, pady=10)
    return frame


def selected_item_id(tree):
    selection = tree.selection()
    if not selection:
        return None
    item = tree.item(selection[0])
    return item["values"][0]
