from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


@dataclass
class VisitorRecord:
    visitor_name: str
    visit_date: str  # YYYY-MM-DD
    arrival_time: str  # HH:MM
    person_visited: str
    reason: str


class VisitorRepository:
    def __init__(self, db_path: str | Path = "visitor_management.db") -> None:
        self.db_path = Path(db_path)
        self._initialize_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS visitors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    visitor_name TEXT NOT NULL,
                    visit_date TEXT NOT NULL,
                    arrival_time TEXT NOT NULL,
                    person_visited TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def add_visitor(self, record: VisitorRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO visitors (
                    visitor_name,
                    visit_date,
                    arrival_time,
                    person_visited,
                    reason
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record.visitor_name,
                    record.visit_date,
                    record.arrival_time,
                    record.person_visited,
                    record.reason,
                ),
            )
            conn.commit()

    def fetch_between(self, start_date: str, end_date: str) -> list[tuple]:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT id, visitor_name, visit_date, arrival_time, person_visited, reason
                FROM visitors
                WHERE visit_date BETWEEN ? AND ?
                ORDER BY visit_date ASC, arrival_time ASC
                """,
                (start_date, end_date),
            )
            return cursor.fetchall()

    def aggregate_top_people(self, start_date: str, end_date: str, limit: int = 5) -> list[tuple[str, int]]:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT person_visited, COUNT(*) AS cnt
                FROM visitors
                WHERE visit_date BETWEEN ? AND ?
                GROUP BY person_visited
                ORDER BY cnt DESC, person_visited ASC
                LIMIT ?
                """,
                (start_date, end_date, limit),
            )
            return cursor.fetchall()

    def aggregate_top_reasons(self, start_date: str, end_date: str, limit: int = 5) -> list[tuple[str, int]]:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT reason, COUNT(*) AS cnt
                FROM visitors
                WHERE visit_date BETWEEN ? AND ?
                GROUP BY reason
                ORDER BY cnt DESC, reason ASC
                LIMIT ?
                """,
                (start_date, end_date, limit),
            )
            return cursor.fetchall()


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_time(value: str) -> datetime.time:
    return datetime.strptime(value, "%H:%M").time()


def get_period_range(period: str, reference_day: date | None = None) -> tuple[date, date]:
    ref = reference_day or date.today()

    if period == "Daily":
        return ref, ref
    if period == "Weekly":
        start = ref - timedelta(days=ref.weekday())
        end = start + timedelta(days=6)
        return start, end
    if period == "Monthly":
        start = ref.replace(day=1)
        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1)
        else:
            next_month = start.replace(month=start.month + 1)
        end = next_month - timedelta(days=1)
        return start, end
    if period == "Yearly":
        start = ref.replace(month=1, day=1)
        end = ref.replace(month=12, day=31)
        return start, end

    raise ValueError(f"Unsupported period: {period}")


def to_iso(d: date) -> str:
    return d.isoformat()
