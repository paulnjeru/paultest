from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from app.reporting import ReportService
from app.storage import VisitorRecord, VisitorRepository, get_period_range, parse_date, parse_time


class StorageReportingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_visitors.db"
        self.repo = VisitorRepository(self.db_path)
        self.service = ReportService(self.repo)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_insert_and_fetch_between(self) -> None:
        self.repo.add_visitor(
            VisitorRecord(
                visitor_name="Alice",
                visit_date="2026-01-15",
                arrival_time="10:30",
                person_visited="Manager",
                reason="Interview",
            )
        )

        rows = self.repo.fetch_between("2026-01-01", "2026-01-31")
        self.assertEqual(1, len(rows))
        self.assertEqual("Alice", rows[0][1])

    def test_aggregations(self) -> None:
        entries = [
            VisitorRecord("A", "2026-01-01", "09:00", "HR", "Interview"),
            VisitorRecord("B", "2026-01-01", "09:15", "HR", "Interview"),
            VisitorRecord("C", "2026-01-01", "09:30", "IT", "Maintenance"),
        ]
        for e in entries:
            self.repo.add_visitor(e)

        people = self.repo.aggregate_top_people("2026-01-01", "2026-01-31")
        reasons = self.repo.aggregate_top_reasons("2026-01-01", "2026-01-31")

        self.assertEqual(("HR", 2), people[0])
        self.assertEqual(("Interview", 2), reasons[0])

    def test_date_time_validation(self) -> None:
        self.assertEqual(2026, parse_date("2026-12-01").year)
        self.assertEqual(14, parse_time("14:10").hour)

    def test_period_range(self) -> None:
        d = date(2026, 3, 18)
        daily = get_period_range("Daily", d)
        weekly = get_period_range("Weekly", d)
        monthly = get_period_range("Monthly", d)
        yearly = get_period_range("Yearly", d)

        self.assertEqual((d, d), daily)
        self.assertEqual(date(2026, 3, 16), weekly[0])
        self.assertEqual(date(2026, 3, 22), weekly[1])
        self.assertEqual(date(2026, 3, 1), monthly[0])
        self.assertEqual(date(2026, 3, 31), monthly[1])
        self.assertEqual(date(2026, 1, 1), yearly[0])
        self.assertEqual(date(2026, 12, 31), yearly[1])


if __name__ == "__main__":
    unittest.main()
