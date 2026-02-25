from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.storage import VisitorRepository, get_period_range, to_iso


@dataclass
class ReportData:
    period: str
    start_date: str
    end_date: str
    total_visits: int
    top_people: list[tuple[str, int]]
    top_reasons: list[tuple[str, int]]
    rows: list[tuple]


class ReportService:
    def __init__(self, repository: VisitorRepository) -> None:
        self.repository = repository

    def generate(self, period: str) -> ReportData:
        start, end = get_period_range(period)
        start_iso, end_iso = to_iso(start), to_iso(end)

        rows = self.repository.fetch_between(start_iso, end_iso)
        top_people = self.repository.aggregate_top_people(start_iso, end_iso)
        top_reasons = self.repository.aggregate_top_reasons(start_iso, end_iso)

        return ReportData(
            period=period,
            start_date=start_iso,
            end_date=end_iso,
            total_visits=len(rows),
            top_people=top_people,
            top_reasons=top_reasons,
            rows=rows,
        )

    def export_excel(self, report: ReportData, destination: str | Path) -> Path:
        path = Path(destination)
        wb = Workbook()
        ws = wb.active
        ws.title = "Visitor Report"

        ws.append(["Period", report.period])
        ws.append(["Date Range", f"{report.start_date} to {report.end_date}"])
        ws.append(["Total Visits", report.total_visits])
        ws.append([])

        ws.append(["Frequently Visited Personnel", "Count"])
        for person, count in report.top_people:
            ws.append([person, count])

        ws.append([])
        ws.append(["Top Reasons", "Count"])
        for reason, count in report.top_reasons:
            ws.append([reason, count])

        ws.append([])
        ws.append(["Visitor Name", "Date", "Time", "Person Visited", "Reason"])
        for _, name, day, time, person, reason in report.rows:
            ws.append([name, day, time, person, reason])

        wb.save(path)
        return path

    def export_pdf(self, report: ReportData, destination: str | Path) -> Path:
        path = Path(destination)
        c = canvas.Canvas(str(path), pagesize=A4)
        width, height = A4
        y = height - 40

        def write_line(text: str, gap: int = 16) -> None:
            nonlocal y
            c.drawString(40, y, text)
            y -= gap

        write_line("Visitor Management Report", 20)
        write_line(f"Period: {report.period}")
        write_line(f"Date Range: {report.start_date} to {report.end_date}")
        write_line(f"Total Visits: {report.total_visits}", 24)

        write_line("Frequently Visited Personnel:")
        if report.top_people:
            for person, count in report.top_people:
                write_line(f"- {person}: {count}")
        else:
            write_line("- No visits")

        write_line("", 10)
        write_line("Top Reasons:")
        if report.top_reasons:
            for reason, count in report.top_reasons:
                write_line(f"- {reason}: {count}")
        else:
            write_line("- No visits")

        c.showPage()
        c.save()
        return path
