from __future__ import annotations

from datetime import date
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, LEFT, X

from app.db import counts, init_db, insert_client, insert_document, insert_loan, list_clients, list_documents, list_loans


class LoanPlatformApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("SimplePay Capital - Loan Management & OCR Platform")
        self.geometry("1320x860")
        self.minsize(1180, 760)

        init_db()
        self.client_map: dict[str, int] = {}

        self._build_header()
        self._build_tabs()
        self.refresh_all()

    def _build_header(self):
        top = ttk.Frame(self, padding=16)
        top.pack(fill=X)
        ttk.Label(top, text="SimplePay Loan Management & OCR Platform", font=("Segoe UI", 22, "bold")).pack(side=LEFT)
        ttk.Label(top, text="Kenya • Uganda • Tanzania", bootstyle="secondary").pack(side=LEFT, padx=15)

    def _build_tabs(self):
        tabs = ttk.Notebook(self)
        tabs.pack(fill=BOTH, expand=True, padx=16, pady=(0, 16))

        self.dashboard_tab = ttk.Frame(tabs)
        self.clients_tab = ttk.Frame(tabs)
        self.loans_tab = ttk.Frame(tabs)
        self.docs_tab = ttk.Frame(tabs)

        tabs.add(self.dashboard_tab, text="Dashboard")
        tabs.add(self.clients_tab, text="Clients & KYC")
        tabs.add(self.loans_tab, text="Loan Management")
        tabs.add(self.docs_tab, text="Document OCR")

        self._build_dashboard()
        self._build_clients()
        self._build_loans()
        self._build_documents()

    def _build_dashboard(self):
        stats_row = ttk.Frame(self.dashboard_tab)
        stats_row.pack(fill=X, pady=10)
        self.stat_labels = {}
        cards = [("clients", "Clients"), ("loans", "Total Loans"), ("active_loans", "Active Loans"), ("documents", "OCR Docs")]
        for key, title in cards:
            card = ttk.Labelframe(stats_row, text=title, bootstyle="info", padding=20)
            card.pack(side=LEFT, fill=X, expand=True, padx=6)
            lbl = ttk.Label(card, text="0", font=("Segoe UI", 28, "bold"))
            lbl.pack()
            self.stat_labels[key] = lbl

    def _build_clients(self):
        form = ttk.Labelframe(self.clients_tab, text="Add Client", padding=12)
        form.pack(fill=X, pady=(10, 6))
        self.client_name = ttk.Entry(form)
        self.client_country = ttk.Combobox(form, values=["Kenya", "Uganda", "Tanzania"], state="readonly")
        self.client_phone = ttk.Entry(form)
        self.client_national_id = ttk.Entry(form)
        for i, (label, widget) in enumerate([
            ("Full Name", self.client_name),
            ("Country", self.client_country),
            ("Phone", self.client_phone),
            ("National ID", self.client_national_id),
        ]):
            ttk.Label(form, text=label).grid(row=0, column=i, sticky="w", padx=4)
            widget.grid(row=1, column=i, sticky="ew", padx=4)
            form.grid_columnconfigure(i, weight=1)
        ttk.Button(form, text="Save Client", bootstyle="success", command=self.add_client).grid(row=1, column=4, padx=8)

        cols = ("full_name", "country", "phone", "national_id")
        self.client_tree = ttk.Treeview(self.clients_tab, columns=cols, show="headings", height=16, bootstyle="info")
        for col, title in zip(cols, ["Name", "Country", "Phone", "National ID"]):
            self.client_tree.heading(col, text=title)
            self.client_tree.column(col, width=250)
        self.client_tree.pack(fill=BOTH, expand=True, pady=6)

    def _build_loans(self):
        form = ttk.Labelframe(self.loans_tab, text="Create Loan", padding=12)
        form.pack(fill=X, pady=(10, 6))
        self.loan_client = ttk.Combobox(form, state="readonly")
        self.loan_principal = ttk.Entry(form)
        self.loan_currency = ttk.Combobox(form, values=["KES", "UGX", "TZS", "USD"], state="readonly")
        self.loan_rate = ttk.Entry(form)
        self.loan_term = ttk.Spinbox(form, from_=1, to=72)
        self.loan_status = ttk.Combobox(form, values=["Pending", "Approved", "Disbursed", "Active", "Closed"], state="readonly")
        self.loan_status.set("Pending")
        self.loan_date = ttk.Entry(form)
        self.loan_date.insert(0, str(date.today()))
        widgets = [self.loan_client, self.loan_principal, self.loan_currency, self.loan_rate, self.loan_term, self.loan_status, self.loan_date]
        labels = ["Client", "Principal", "Currency", "Interest %", "Term (months)", "Status", "Disbursed Date"]
        for i, (label, widget) in enumerate(zip(labels, widgets)):
            ttk.Label(form, text=label).grid(row=0, column=i, sticky="w", padx=3)
            widget.grid(row=1, column=i, sticky="ew", padx=3)
            form.grid_columnconfigure(i, weight=1)
        ttk.Button(form, text="Save Loan", bootstyle="success", command=self.add_loan).grid(row=1, column=7, padx=8)

        cols = ("id", "client_name", "country", "principal", "currency", "interest_rate", "term_months", "status", "outstanding_balance")
        self.loan_tree = ttk.Treeview(self.loans_tab, columns=cols, show="headings", height=16, bootstyle="warning")
        for col, title, width in [
            ("id", "Loan #", 70), ("client_name", "Client", 200), ("country", "Country", 120), ("principal", "Principal", 120),
            ("currency", "Currency", 80), ("interest_rate", "Rate%", 80), ("term_months", "Term", 80), ("status", "Status", 120), ("outstanding_balance", "Outstanding", 140)
        ]:
            self.loan_tree.heading(col, text=title)
            self.loan_tree.column(col, width=width)
        self.loan_tree.pack(fill=BOTH, expand=True, pady=6)

    def _build_documents(self):
        form = ttk.Labelframe(self.docs_tab, text="Upload Document Metadata + OCR Text", padding=12)
        form.pack(fill=X, pady=(10, 6))
        self.doc_client = ttk.Combobox(form, state="readonly")
        self.doc_loan = ttk.Entry(form)
        self.doc_type = ttk.Combobox(form, values=["Logbook", "Title Deed", "National ID", "Other"], state="readonly")
        self.doc_number = ttk.Entry(form)
        self.doc_file = ttk.Entry(form)
        self.doc_ocr = ttk.Entry(form)
        widgets = [self.doc_client, self.doc_loan, self.doc_type, self.doc_number, self.doc_file, self.doc_ocr]
        labels = ["Client", "Loan # (optional)", "Doc Type", "Doc Number", "File Reference", "OCR Extract"]
        for i, (label, widget) in enumerate(zip(labels, widgets)):
            ttk.Label(form, text=label).grid(row=0, column=i, sticky="w", padx=3)
            widget.grid(row=1, column=i, sticky="ew", padx=3)
            form.grid_columnconfigure(i, weight=1)
        ttk.Button(form, text="Save Document", bootstyle="success", command=self.add_document).grid(row=1, column=6, padx=8)

        cols = ("client_name", "loan_id", "document_type", "document_number", "file_reference", "uploaded_on")
        self.doc_tree = ttk.Treeview(self.docs_tab, columns=cols, show="headings", height=16, bootstyle="success")
        for col, title, width in [
            ("client_name", "Client", 200), ("loan_id", "Loan #", 80), ("document_type", "Type", 110),
            ("document_number", "Document No.", 160), ("file_reference", "File Reference", 260), ("uploaded_on", "Uploaded", 110)
        ]:
            self.doc_tree.heading(col, text=title)
            self.doc_tree.column(col, width=width)
        self.doc_tree.pack(fill=BOTH, expand=True, pady=6)

    def add_client(self):
        try:
            insert_client(self.client_name.get(), self.client_country.get(), self.client_phone.get(), self.client_national_id.get())
            self.client_name.delete(0, "end")
            self.client_phone.delete(0, "end")
            self.client_national_id.delete(0, "end")
            self.client_country.set("")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Could not add client", str(exc))

    def add_loan(self):
        client_id = self.client_map.get(self.loan_client.get())
        if not client_id:
            messagebox.showwarning("Missing data", "Select a client.")
            return
        try:
            insert_loan(client_id, float(self.loan_principal.get()), self.loan_currency.get(), float(self.loan_rate.get()), int(self.loan_term.get()), self.loan_status.get(), self.loan_date.get())
            self.loan_principal.delete(0, "end")
            self.loan_rate.delete(0, "end")
            self.loan_term.delete(0, "end")
            self.loan_term.insert(0, "12")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Could not add loan", str(exc))

    def add_document(self):
        client_id = self.client_map.get(self.doc_client.get())
        if not client_id:
            messagebox.showwarning("Missing data", "Select a client.")
            return
        loan_raw = self.doc_loan.get().strip()
        loan_id = int(loan_raw) if loan_raw else None
        try:
            insert_document(client_id, loan_id, self.doc_type.get(), self.doc_number.get(), self.doc_file.get(), self.doc_ocr.get(), str(date.today()))
            self.doc_loan.delete(0, "end")
            self.doc_number.delete(0, "end")
            self.doc_file.delete(0, "end")
            self.doc_ocr.delete(0, "end")
            self.doc_type.set("")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Could not add document", str(exc))

    def refresh_all(self):
        clients = list_clients()
        loans = list_loans()
        docs = list_documents()

        self.client_map = {f"{row['full_name']} ({row['country']})": row["id"] for row in clients}
        labels = list(self.client_map.keys())
        self.loan_client["values"] = labels
        self.doc_client["values"] = labels

        for tree in [self.client_tree, self.loan_tree, self.doc_tree]:
            for row in tree.get_children():
                tree.delete(row)

        for row in clients:
            self.client_tree.insert("", "end", values=(row["full_name"], row["country"], row["phone"], row["national_id"]))
        for row in loans:
            self.loan_tree.insert("", "end", values=(row["id"], row["client_name"], row["country"], row["principal"], row["currency"], row["interest_rate"], row["term_months"], row["status"], row["outstanding_balance"]))
        for row in docs:
            self.doc_tree.insert("", "end", values=(row["client_name"], row["loan_id"] or "-", row["document_type"], row["document_number"], row["file_reference"], row["uploaded_on"]))

        stats = counts()
        for key, lbl in self.stat_labels.items():
            lbl.config(text=str(stats[key]))


if __name__ == "__main__":
    app = LoanPlatformApp()
    app.mainloop()
