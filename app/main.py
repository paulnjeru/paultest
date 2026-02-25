from __future__ import annotations

import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import messagebox, ttk

from app.reporting import ReportService
from app.storage import VisitorRecord, VisitorRepository, parse_date, parse_time


class VisitorManagementApp:
    def __init__(self, root: tk.Tk, can_modify: bool = True) -> None:
        self.root = root
        self.root.title("Front Office Visitor Management")
        self.root.geometry("760x560")

        self.repository = VisitorRepository()
        self.report_service = ReportService(self.repository)
        self.can_modify = can_modify

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(container, text="Front Office Visitor Form", font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        self.fields: dict[str, tk.StringVar] = {
            "Visitor's Name": tk.StringVar(),
            "Date of Visit (YYYY-MM-DD)": tk.StringVar(value=date.today().isoformat()),
            "Time of Arrival (HH:MM)": tk.StringVar(),
            "Person Being Visited": tk.StringVar(),
            "Reason for Visit": tk.StringVar(),
        }

        for idx, (label, variable) in enumerate(self.fields.items(), start=1):
            ttk.Label(container, text=label).grid(row=idx, column=0, sticky="w", pady=6)
            ttk.Entry(container, textvariable=variable, width=44).grid(row=idx, column=1, sticky="w", pady=6)

        submit_btn = ttk.Button(container, text="Submit", command=self.submit)
        submit_btn.grid(row=7, column=0, pady=12, sticky="w")
        if not self.can_modify:
            submit_btn.state(["disabled"])

        ttk.Separator(container, orient="horizontal").grid(row=8, column=0, columnspan=2, sticky="ew", pady=14)

        ttk.Label(container, text="Generate Reports", font=("Segoe UI", 12, "bold")).grid(
            row=9, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )

        self.period_var = tk.StringVar(value="Daily")
        ttk.Label(container, text="Period").grid(row=10, column=0, sticky="w", pady=4)
        ttk.Combobox(
            container,
            textvariable=self.period_var,
            values=["Daily", "Weekly", "Monthly", "Yearly"],
            state="readonly",
            width=20,
        ).grid(row=10, column=1, sticky="w", pady=4)

        ttk.Button(container, text="Generate Report", command=self.generate_report).grid(row=11, column=0, sticky="w", pady=8)

        self.report_text = tk.Text(container, width=85, height=14, state=tk.DISABLED)
        self.report_text.grid(row=12, column=0, columnspan=2, pady=8)

        export_container = ttk.Frame(container)
        export_container.grid(row=13, column=0, columnspan=2, sticky="w", pady=6)

        ttk.Button(export_container, text="Export PDF", command=self.export_pdf).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(export_container, text="Export Excel", command=self.export_excel).grid(row=0, column=1)

        self.last_report = None

    def submit(self) -> None:
        try:
            values = {k: v.get().strip() for k, v in self.fields.items()}
            for label, value in values.items():
                if not value:
                    raise ValueError(f"{label} is required.")

            parse_date(values["Date of Visit (YYYY-MM-DD)"])
            parse_time(values["Time of Arrival (HH:MM)"])

            record = VisitorRecord(
                visitor_name=values["Visitor's Name"],
                visit_date=values["Date of Visit (YYYY-MM-DD)"],
                arrival_time=values["Time of Arrival (HH:MM)"],
                person_visited=values["Person Being Visited"],
                reason=values["Reason for Visit"],
            )
            self.repository.add_visitor(record)
            messagebox.showinfo("Saved", "Visitor information saved successfully.")

            for label, var in self.fields.items():
                if label == "Date of Visit (YYYY-MM-DD)":
                    var.set(date.today().isoformat())
                else:
                    var.set("")
        except ValueError as exc:
            messagebox.showerror("Validation Error", str(exc))

    def generate_report(self) -> None:
        try:
            report = self.report_service.generate(self.period_var.get())
            self.last_report = report
            self._render_report(report)
            messagebox.showinfo("Report", "Report generated successfully.")
        except Exception as exc:  # user-facing guardrail
            messagebox.showerror("Report Error", str(exc))

    def _render_report(self, report) -> None:
        lines = [
            f"Period: {report.period}",
            f"Date Range: {report.start_date} to {report.end_date}",
            f"Total Visits: {report.total_visits}",
            "",
            "Frequently Visited Personnel:",
        ]
        if report.top_people:
            lines.extend([f"  - {name}: {count}" for name, count in report.top_people])
        else:
            lines.append("  - No visits")

        lines.extend(["", "Top Reasons for Visit:"])
        if report.top_reasons:
            lines.extend([f"  - {reason}: {count}" for reason, count in report.top_reasons])
        else:
            lines.append("  - No visits")

        self.report_text.configure(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, "\n".join(lines))
        self.report_text.configure(state=tk.DISABLED)

    def export_pdf(self) -> None:
        if not self.last_report:
            messagebox.showwarning("No Report", "Generate a report before exporting.")
            return
        path = Path(f"visitor_report_{self.last_report.period.lower()}.pdf")
        self.report_service.export_pdf(self.last_report, path)
        messagebox.showinfo("Export Complete", f"PDF report exported to {path.resolve()}")

    def export_excel(self) -> None:
        if not self.last_report:
            messagebox.showwarning("No Report", "Generate a report before exporting.")
            return
        path = Path(f"visitor_report_{self.last_report.period.lower()}.xlsx")
        self.report_service.export_excel(self.last_report, path)
        messagebox.showinfo("Export Complete", f"Excel report exported to {path.resolve()}")


def authenticate_user() -> tuple[bool, str]:
    accounts = {
        "admin": "admin123",
        "viewer": "viewer123",
    }

    login = tk.Tk()
    login.title("Login")
    login.geometry("320x180")
    login.resizable(False, False)

    username_var = tk.StringVar()
    password_var = tk.StringVar()
    result = {"ok": False, "role": "viewer"}

    frame = ttk.Frame(login, padding=16)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="Username").grid(row=0, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=username_var).grid(row=0, column=1, pady=4)

    ttk.Label(frame, text="Password").grid(row=1, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=password_var, show="*").grid(row=1, column=1, pady=4)

    def attempt_login() -> None:
        username = username_var.get().strip()
        password = password_var.get().strip()

        if accounts.get(username) == password:
            result["ok"] = True
            result["role"] = username
            login.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    ttk.Button(frame, text="Login", command=attempt_login).grid(row=2, column=0, columnspan=2, pady=10)

    login.mainloop()
    return result["ok"], result["role"]


def main() -> None:
    ok, role = authenticate_user()
    if not ok:
        return

    root = tk.Tk()
    app = VisitorManagementApp(root, can_modify=(role == "admin"))
    root.mainloop()


if __name__ == "__main__":
    main()
