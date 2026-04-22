import sqlite3
from pathlib import Path

DB_PATH = Path("data") / "inventory.db"


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_tag TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                purchase_date TEXT NOT NULL,
                assigned_to INTEGER,
                status TEXT NOT NULL DEFAULT 'Available',
                FOREIGN KEY(assigned_to) REFERENCES employees(id)
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                vendor TEXT NOT NULL,
                requested_by INTEGER NOT NULL,
                ordered_by INTEGER NOT NULL,
                status TEXT NOT NULL,
                ordered_date TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY(requested_by) REFERENCES employees(id),
                FOREIGN KEY(ordered_by) REFERENCES employees(id)
            );
            """
        )


def insert_employee(name: str, department: str, email: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO employees(name, department, email) VALUES (?, ?, ?)",
            (name.strip(), department.strip(), email.strip()),
        )


def insert_item(asset_tag: str, name: str, category: str, purchase_date: str, assigned_to: int | None):
    status = "Assigned" if assigned_to else "Available"
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO items(asset_tag, name, category, purchase_date, assigned_to, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (asset_tag.strip(), name.strip(), category.strip(), purchase_date, assigned_to, status),
        )


def assign_item(item_id: int, employee_id: int | None):
    status = "Assigned" if employee_id else "Available"
    with get_conn() as conn:
        conn.execute(
            "UPDATE items SET assigned_to = ?, status = ? WHERE id = ?",
            (employee_id, status, item_id),
        )


def insert_order(
    item_name: str,
    quantity: int,
    vendor: str,
    requested_by: int,
    ordered_by: int,
    status: str,
    ordered_date: str,
    notes: str,
):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO orders(item_name, quantity, vendor, requested_by, ordered_by, status, ordered_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (item_name.strip(), quantity, vendor.strip(), requested_by, ordered_by, status, ordered_date, notes.strip()),
        )


def list_employees():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM employees ORDER BY name").fetchall()


def list_items():
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT i.*, e.name AS assigned_name
            FROM items i
            LEFT JOIN employees e ON e.id = i.assigned_to
            ORDER BY i.asset_tag
            """
        ).fetchall()


def list_orders():
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT o.*, req.name AS requested_name, ord.name AS ordered_name
            FROM orders o
            JOIN employees req ON req.id = o.requested_by
            JOIN employees ord ON ord.id = o.ordered_by
            ORDER BY o.ordered_date DESC
            """
        ).fetchall()


def counts():
    with get_conn() as conn:
        employees = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        items = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        assigned = conn.execute("SELECT COUNT(*) FROM items WHERE assigned_to IS NOT NULL").fetchone()[0]
        orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        return {"employees": employees, "items": items, "assigned": assigned, "orders": orders}
