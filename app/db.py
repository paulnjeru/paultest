import sqlite3
from pathlib import Path

DB_PATH = Path("data") / "simplepay_platform.db"


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                country TEXT NOT NULL,
                phone TEXT NOT NULL,
                national_id TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                principal REAL NOT NULL,
                currency TEXT NOT NULL,
                interest_rate REAL NOT NULL,
                term_months INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                disbursed_on TEXT,
                outstanding_balance REAL NOT NULL,
                FOREIGN KEY(client_id) REFERENCES clients(id)
            );

            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                loan_id INTEGER,
                document_type TEXT NOT NULL,
                document_number TEXT,
                file_reference TEXT,
                ocr_text TEXT,
                uploaded_on TEXT NOT NULL,
                FOREIGN KEY(client_id) REFERENCES clients(id),
                FOREIGN KEY(loan_id) REFERENCES loans(id)
            );
            """
        )


def insert_client(full_name: str, country: str, phone: str, national_id: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO clients(full_name, country, phone, national_id) VALUES (?, ?, ?, ?)",
            (full_name.strip(), country.strip(), phone.strip(), national_id.strip()),
        )


def insert_loan(client_id: int, principal: float, currency: str, interest_rate: float, term_months: int, status: str, disbursed_on: str):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO loans(client_id, principal, currency, interest_rate, term_months, status, disbursed_on, outstanding_balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (client_id, principal, currency, interest_rate, term_months, status, disbursed_on, principal),
        )


def insert_document(client_id: int, loan_id: int | None, document_type: str, document_number: str, file_reference: str, ocr_text: str, uploaded_on: str):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO documents(client_id, loan_id, document_type, document_number, file_reference, ocr_text, uploaded_on)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (client_id, loan_id, document_type.strip(), document_number.strip(), file_reference.strip(), ocr_text.strip(), uploaded_on),
        )


def list_clients():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM clients ORDER BY full_name").fetchall()


def list_loans():
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT l.*, c.full_name AS client_name, c.country
            FROM loans l
            JOIN clients c ON c.id = l.client_id
            ORDER BY l.id DESC
            """
        ).fetchall()


def list_documents():
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT d.*, c.full_name AS client_name
            FROM documents d
            JOIN clients c ON c.id = d.client_id
            ORDER BY d.uploaded_on DESC, d.id DESC
            """
        ).fetchall()


def counts():
    with get_conn() as conn:
        clients = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        loans = conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0]
        active_loans = conn.execute("SELECT COUNT(*) FROM loans WHERE status IN ('Approved','Disbursed','Active')").fetchone()[0]
        documents = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        return {"clients": clients, "loans": loans, "active_loans": active_loans, "documents": documents}
