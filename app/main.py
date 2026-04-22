from __future__ import annotations

import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import messagebox
from urllib.request import urlretrieve

import ttkbootstrap as ttk
from PIL import Image, ImageTk
from ttkbootstrap.constants import BOTH, LEFT, RIGHT, X

from app.db import (
    assign_item,
    counts,
    init_db,
    insert_employee,
    insert_item,
    insert_order,
    list_employees,
    list_items,
    list_orders,
)

ASSETS = {
    "hero": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Dell_Servers.jpg/1280px-Dell_Servers.jpg",
    "inventory": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Laptop_and_mouse.jpg/1280px-Laptop_and_mouse.jpg",
}
ASSET_DIR = Path("assets")


def ensure_assets():
    ASSET_DIR.mkdir(exist_ok=True)
    for name, url in ASSETS.items():
        target = ASSET_DIR / f"{name}.jpg"
        if not target.exists():
            try:
                urlretrieve(url, target)
            except Exception:
                continue


class InventoryApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("IT Inventory & Procurement Hub")
        self.geometry("1320x860")
        self.minsize(1180, 760)

        init_db()
        ensure_assets()

        self.employee_map: dict[str, int] = {}
        self.item_map: dict[str, int] = {}

        self._build_header()
        self._build_tabs()
        self.refresh_all()

    def _build_header(self):
        top = ttk.Frame(self, padding=16)
        top.pack(fill=X)

        ttk.Label(top, text="IT Inventory & Procurement Hub", font=("Segoe UI", 22, "bold")).pack(side=LEFT)
        ttk.Label(top, text="Track assets, assignees, and purchasing ownership.", bootstyle="secondary").pack(side=LEFT, padx=15)

    def _build_tabs(self):
        tabs = ttk.Notebook(self)
        tabs.pack(fill=BOTH, expand=True, padx=16, pady=(0, 16))

        self.dashboard_tab = ttk.Frame(tabs)
        self.inventory_tab = ttk.Frame(tabs)
        self.employee_tab = ttk.Frame(tabs)
        self.orders_tab = ttk.Frame(tabs)

        tabs.add(self.dashboard_tab, text="Dashboard")
        tabs.add(self.inventory_tab, text="Inventory")
        tabs.add(self.employee_tab, text="Employees")
        tabs.add(self.orders_tab, text="Orders")

        self._build_dashboard()
        self._build_employees()
        self._build_inventory()
        self._build_orders()

    def _build_dashboard(self):
        stats_row = ttk.Frame(self.dashboard_tab)
        stats_row.pack(fill=X, pady=10)

        self.stat_labels = {}
        cards = [("employees", "Employees"), ("items", "Total Assets"), ("assigned", "Assigned Assets"), ("orders", "Purchase Orders")]
        for key, title in cards:
            card = ttk.Labelframe(stats_row, text=title, bootstyle="info", padding=20)
            card.pack(side=LEFT, fill=X, expand=True, padx=6)
            lbl = ttk.Label(card, text="0", font=("Segoe UI", 28, "bold"))
            lbl.pack()
            self.stat_labels[key] = lbl

        hero_wrap = ttk.Frame(self.dashboard_tab)
        hero_wrap.pack(fill=BOTH, expand=True, pady=10)
        img_path = ASSET_DIR / "hero.jpg"
        if img_path.exists():
            image = Image.open(img_path).resize((1200, 440))
            self.hero_photo = ImageTk.PhotoImage(image)
            canvas = tk.Canvas(hero_wrap, height=440, highlightthickness=0)
            canvas.pack(fill=BOTH, expand=True)
            canvas.create_image(0, 0, anchor="nw", image=self.hero_photo)
            canvas.create_rectangle(0, 0, 1200, 440, fill="#0d1b2a", stipple="gray50", outline="")
            canvas.create_text(
                34,
                48,
                anchor="nw",
                fill="white",
                width=700,
                text="Centralize who owns each IT asset and who is accountable for each purchase order.",
                font=("Segoe UI", 24, "bold"),
            )
            canvas.create_text(
                34,
                170,
                anchor="nw",
                fill="white",
                width=660,
                text="Use the tabs above to add staff, register laptops/monitors/peripherals, assign equipment, and track procurement workflows.",
                font=("Segoe UI", 13),
            )

    def _build_employees(self):
        form = ttk.Labelframe(self.employee_tab, text="Add Employee", padding=12)
        form.pack(fill=X, pady=(10, 6))

        self.emp_name = ttk.Entry(form)
        self.emp_dept = ttk.Entry(form)
        self.emp_email = ttk.Entry(form)
        for i, (label, widget) in enumerate(
            [("Name", self.emp_name), ("Department", self.emp_dept), ("Email", self.emp_email)]
        ):
            ttk.Label(form, text=label).grid(row=0, column=i, sticky="w", padx=4)
            widget.grid(row=1, column=i, sticky="ew", padx=4)
            form.grid_columnconfigure(i, weight=1)

        ttk.Button(form, text="Add Employee", bootstyle="success", command=self.add_employee).grid(row=1, column=3, padx=8)

        cols = ("name", "department", "email")
        self.emp_tree = ttk.Treeview(self.employee_tab, columns=cols, show="headings", height=16, bootstyle="info")
        for col, title in zip(cols, ["Name", "Department", "Email"]):
            self.emp_tree.heading(col, text=title)
            self.emp_tree.column(col, width=260)
        self.emp_tree.pack(fill=BOTH, expand=True, pady=6)

    def _build_inventory(self):
        top = ttk.Labelframe(self.inventory_tab, text="Register Asset", padding=12)
        top.pack(fill=X, pady=(10, 6))

        self.item_asset = ttk.Entry(top)
        self.item_name = ttk.Entry(top)
        self.item_category = ttk.Entry(top)
        self.item_date = ttk.Entry(top)
        self.item_date.insert(0, str(date.today()))
        self.item_assignee = ttk.Combobox(top, state="readonly")

        labels = ["Asset Tag", "Item Name", "Category", "Purchase Date", "Assign To"]
        widgets = [self.item_asset, self.item_name, self.item_category, self.item_date, self.item_assignee]
        for i, (label, widget) in enumerate(zip(labels, widgets)):
            ttk.Label(top, text=label).grid(row=0, column=i, sticky="w", padx=4)
            widget.grid(row=1, column=i, sticky="ew", padx=4)
            top.grid_columnconfigure(i, weight=1)

        ttk.Button(top, text="Add Asset", bootstyle="success", command=self.add_item).grid(row=1, column=5, padx=8)

        assign = ttk.Labelframe(self.inventory_tab, text="Assign Existing Asset", padding=12)
        assign.pack(fill=X, pady=(0, 6))

        self.assign_item_combo = ttk.Combobox(assign, state="readonly")
        self.assign_employee_combo = ttk.Combobox(assign, state="readonly")
        ttk.Label(assign, text="Asset").grid(row=0, column=0, sticky="w")
        ttk.Label(assign, text="Employee").grid(row=0, column=1, sticky="w")
        self.assign_item_combo.grid(row=1, column=0, sticky="ew", padx=4)
        self.assign_employee_combo.grid(row=1, column=1, sticky="ew", padx=4)
        assign.grid_columnconfigure(0, weight=1)
        assign.grid_columnconfigure(1, weight=1)
        ttk.Button(assign, text="Save Assignment", bootstyle="primary", command=self.save_assignment).grid(row=1, column=2, padx=8)

        cols = ("asset_tag", "name", "category", "status", "assigned_name")
        self.item_tree = ttk.Treeview(self.inventory_tab, columns=cols, show="headings", height=15, bootstyle="warning")
        for col, title, width in [
            ("asset_tag", "Asset Tag", 130),
            ("name", "Item", 240),
            ("category", "Category", 160),
            ("status", "Status", 120),
            ("assigned_name", "Assigned To", 220),
        ]:
            self.item_tree.heading(col, text=title)
            self.item_tree.column(col, width=width)
        self.item_tree.pack(fill=BOTH, expand=True, pady=6)

    def _build_orders(self):
        form = ttk.Labelframe(self.orders_tab, text="Create Purchase Order", padding=12)
        form.pack(fill=X, pady=(10, 6))

        self.order_item = ttk.Entry(form)
        self.order_qty = ttk.Spinbox(form, from_=1, to=999)
        self.order_vendor = ttk.Entry(form)
        self.order_requested = ttk.Combobox(form, state="readonly")
        self.order_ordered = ttk.Combobox(form, state="readonly")
        self.order_status = ttk.Combobox(form, state="readonly", values=["Requested", "Placed", "Delivered", "Cancelled"])
        self.order_status.set("Requested")
        self.order_date = ttk.Entry(form)
        self.order_date.insert(0, str(date.today()))
        self.order_notes = ttk.Entry(form)

        labels = [
            "Item",
            "Qty",
            "Vendor",
            "Requested By",
            "Ordered By",
            "Status",
            "Date",
            "Notes",
        ]
        widgets = [
            self.order_item,
            self.order_qty,
            self.order_vendor,
            self.order_requested,
            self.order_ordered,
            self.order_status,
            self.order_date,
            self.order_notes,
        ]
        for i, (label, widget) in enumerate(zip(labels, widgets)):
            ttk.Label(form, text=label).grid(row=0, column=i, sticky="w", padx=3)
            widget.grid(row=1, column=i, sticky="ew", padx=3)
            form.grid_columnconfigure(i, weight=1)

        ttk.Button(form, text="Add Order", bootstyle="success", command=self.add_order).grid(row=1, column=8, padx=8)

        cols = ("item_name", "quantity", "vendor", "requested_name", "ordered_name", "status", "ordered_date")
        self.order_tree = ttk.Treeview(self.orders_tab, columns=cols, show="headings", height=16, bootstyle="success")
        for col, title, width in [
            ("item_name", "Item", 220),
            ("quantity", "Qty", 60),
            ("vendor", "Vendor", 160),
            ("requested_name", "Requested By", 170),
            ("ordered_name", "Ordered By", 170),
            ("status", "Status", 110),
            ("ordered_date", "Date", 110),
        ]:
            self.order_tree.heading(col, text=title)
            self.order_tree.column(col, width=width)
        self.order_tree.pack(fill=BOTH, expand=True, pady=6)

    def add_employee(self):
        try:
            insert_employee(self.emp_name.get(), self.emp_dept.get(), self.emp_email.get())
            self.emp_name.delete(0, "end")
            self.emp_dept.delete(0, "end")
            self.emp_email.delete(0, "end")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Could not add employee", str(exc))

    def add_item(self):
        assignee = self.employee_map.get(self.item_assignee.get())
        try:
            insert_item(
                self.item_asset.get(),
                self.item_name.get(),
                self.item_category.get(),
                self.item_date.get(),
                assignee,
            )
            self.item_asset.delete(0, "end")
            self.item_name.delete(0, "end")
            self.item_category.delete(0, "end")
            self.item_date.delete(0, "end")
            self.item_date.insert(0, str(date.today()))
            self.item_assignee.set("")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Could not add asset", str(exc))

    def save_assignment(self):
        item_id = self.item_map.get(self.assign_item_combo.get())
        employee_id = self.employee_map.get(self.assign_employee_combo.get())
        if not item_id or not employee_id:
            messagebox.showwarning("Missing data", "Select both asset and employee.")
            return
        assign_item(item_id, employee_id)
        self.refresh_all()

    def add_order(self):
        requested_by = self.employee_map.get(self.order_requested.get())
        ordered_by = self.employee_map.get(self.order_ordered.get())
        if not requested_by or not ordered_by:
            messagebox.showwarning("Missing data", "Select requestor and purchaser.")
            return
        try:
            insert_order(
                self.order_item.get(),
                int(self.order_qty.get()),
                self.order_vendor.get(),
                requested_by,
                ordered_by,
                self.order_status.get(),
                self.order_date.get(),
                self.order_notes.get(),
            )
            self.order_item.delete(0, "end")
            self.order_qty.delete(0, "end")
            self.order_qty.insert(0, "1")
            self.order_vendor.delete(0, "end")
            self.order_status.set("Requested")
            self.order_date.delete(0, "end")
            self.order_date.insert(0, str(date.today()))
            self.order_notes.delete(0, "end")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Could not add order", str(exc))

    def refresh_all(self):
        people = list_employees()
        items = list_items()
        orders = list_orders()

        self.employee_map = {f"{row['name']} ({row['department']})": row["id"] for row in people}
        self.item_map = {f"{row['asset_tag']} - {row['name']}": row["id"] for row in items}

        people_labels = list(self.employee_map.keys())
        self.item_assignee["values"] = [""] + people_labels
        self.assign_employee_combo["values"] = people_labels
        self.order_requested["values"] = people_labels
        self.order_ordered["values"] = people_labels

        self.assign_item_combo["values"] = list(self.item_map.keys())

        for tree in [self.emp_tree, self.item_tree, self.order_tree]:
            for row in tree.get_children():
                tree.delete(row)

        for row in people:
            self.emp_tree.insert("", "end", values=(row["name"], row["department"], row["email"]))

        for row in items:
            self.item_tree.insert(
                "", "end", values=(row["asset_tag"], row["name"], row["category"], row["status"], row["assigned_name"] or "Unassigned")
            )

        for row in orders:
            self.order_tree.insert(
                "",
                "end",
                values=(
                    row["item_name"],
                    row["quantity"],
                    row["vendor"],
                    row["requested_name"],
                    row["ordered_name"],
                    row["status"],
                    row["ordered_date"],
                ),
            )

        stats = counts()
        for key, lbl in self.stat_labels.items():
            lbl.config(text=str(stats[key]))


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
