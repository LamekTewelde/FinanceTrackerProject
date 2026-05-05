"""
Central database layer for the finance tracker application.
"""

import sqlite3
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(__file__).resolve().parent / "finance.db"


class FinanceDatabase:
    """Small database service class that encapsulates all SQLite access."""

    # This method stores the database file path and makes the class ready to use.
    # Params: db_path (optional custom path to the SQLite file).
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH

    # This method opens and returns a sqlite3 connection for one operation.
    # Params: none.
    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    # This method creates all required tables if they do not already exist.
    # Params: none.
    def init_db(self):
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                    UNIQUE(name, type)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    note TEXT
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL UNIQUE,
                    monthly_limit REAL NOT NULL CHECK (monthly_limit > 0)
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    # This method returns transaction rows with optional filters.
    # Params: filters (optional dict with type, category, date_start, date_end keys).
    def get_transactions(self, filters: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        filters = filters or {}
        conn = self._connect()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = "SELECT id, amount, type, category, date, note FROM transactions WHERE 1=1"
            params: list[Any] = []
            if filters.get("type"):
                query += " AND type = ?"
                params.append(filters["type"])
            if filters.get("category"):
                query += " AND category = ?"
                params.append(filters["category"])
            if filters.get("date_start"):
                query += " AND date >= ?"
                params.append(filters["date_start"])
            if filters.get("date_end"):
                query += " AND date <= ?"
                params.append(filters["date_end"])
            query += " ORDER BY date DESC, id DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # This method inserts one transaction record.
    # Params: amount (float), type (income or expense), category (str), date (YYYY-MM-DD), note (optional str).
    def add_transaction(
        self,
        amount: float,
        type: str,
        category: str,
        date: str,
        note: Optional[str],
    ):
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO transactions (amount, type, category, date, note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (amount, type, category, date, note or ""),
            )
            conn.commit()
        finally:
            conn.close()

    # This method deletes one transaction by id.
    # Params: id (integer transaction primary key).
    def delete_transaction(self, id: int):
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (id,))
            conn.commit()
        finally:
            conn.close()

    # This method computes total income, total expense, and net amount in a date range.
    # Params: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD).
    def get_summary(self, start_date: str, end_date: str) -> dict[str, float]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COALESCE(SUM(amount), 0) FROM transactions
                WHERE type = 'income' AND date >= ? AND date <= ?
                """,
                (start_date, end_date),
            )
            income = float(cursor.fetchone()[0])
            cursor.execute(
                """
                SELECT COALESCE(SUM(amount), 0) FROM transactions
                WHERE type = 'expense' AND date >= ? AND date <= ?
                """,
                (start_date, end_date),
            )
            expense = float(cursor.fetchone()[0])
            return {"income": income, "expense": expense, "net": income - expense}
        finally:
            conn.close()

    # This method returns monthly income and expense totals for recent months.
    # Params: months (how many recent months to include, default 6).
    def get_monthly_trends(self, months: int = 6) -> list[tuple[str, float, float]]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT strftime('%Y-%m', date) AS ym,
                       SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS income_total,
                       SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS expense_total
                FROM transactions
                WHERE date >= date('now', ?)
                GROUP BY ym
                ORDER BY ym
                """,
                (f"-{months} months",),
            )
            rows = cursor.fetchall()
            return [(row[0], float(row[1]), float(row[2])) for row in rows]
        finally:
            conn.close()

    # This method returns monthly income and expense totals inside a custom date range.
    # Params: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD).
    def get_monthly_trends_for_range(self, start_date: str, end_date: str) -> list[tuple[str, float, float]]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT strftime('%Y-%m', date) AS ym,
                       SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END),
                       SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END)
                FROM transactions
                WHERE date >= ? AND date <= ?
                GROUP BY ym
                ORDER BY ym
                """,
                (start_date, end_date),
            )
            return [(row[0], float(row[1]), float(row[2])) for row in cursor.fetchall()]
        finally:
            conn.close()

    # This method returns expense totals grouped by category for a date range.
    # Params: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD).
    def get_expense_totals_by_category(self, start_date: str, end_date: str) -> list[tuple[str, float]]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT category, SUM(amount) AS total
                FROM transactions
                WHERE type = 'expense' AND date >= ? AND date <= ?
                GROUP BY category
                ORDER BY total DESC
                """,
                (start_date, end_date),
            )
            return [(row[0], float(row[1])) for row in cursor.fetchall()]
        finally:
            conn.close()

    # This method returns all categories sorted for UI display.
    # Params: none.
    def get_categories(self) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, type
                FROM categories
                ORDER BY type, name
                """
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # This method returns category names for one category type.
    # Params: type (income or expense).
    def get_category_names(self, type: str) -> list[str]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM categories WHERE type = ? ORDER BY name",
                (type,),
            )
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    # This method inserts one category record.
    # Params: name (str), type (income or expense).
    def add_category(self, name: str, type: str):
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO categories (name, type)
                VALUES (?, ?)
                """,
                (name.strip(), type),
            )
            conn.commit()
        finally:
            conn.close()

    # This method deletes a category only if no transactions currently use it.
    # Params: id (integer category primary key).
    def delete_category(self, id: int) -> bool:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name, type FROM categories WHERE id = ?", (id,))
            row = cursor.fetchone()
            if not row:
                return False
            name, category_type = row
            cursor.execute(
                """
                SELECT COUNT(*) FROM transactions
                WHERE category = ? AND type = ?
                """,
                (name, category_type),
            )
            if cursor.fetchone()[0] > 0:
                return False
            cursor.execute("DELETE FROM categories WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # This method counts how many transactions use one category name/type pair.
    # Params: name (category string), type (income or expense).
    def count_transactions_for_category(self, name: str, type: str) -> int:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM transactions
                WHERE category = ? AND type = ?
                """,
                (name, type),
            )
            return int(cursor.fetchone()[0])
        finally:
            conn.close()

    # This method returns the earliest and latest transaction dates.
    # Params: none.
    def get_transaction_date_bounds(self) -> tuple[Optional[str], Optional[str]]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MIN(date), MAX(date) FROM transactions")
            row = cursor.fetchone()
            if not row or row[0] is None:
                return None, None
            return row[0], row[1]
        finally:
            conn.close()

    # This method runs a read-only SQL query and returns rows as dictionaries.
    # Params: query (SQL string), params (optional list/tuple of query values).
    def fetch_sql(self, query: str, params: Optional[tuple[Any, ...]] = None) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # This method creates or updates a monthly spending limit for one category.
    # Params: category (expense category name), monthly_limit (positive amount).
    def upsert_budget(self, category: str, monthly_limit: float):
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO budgets (category, monthly_limit)
                VALUES (?, ?)
                ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit
                """,
                (category, monthly_limit),
            )
            conn.commit()
        finally:
            conn.close()

    # This method returns all stored budget limits ordered by category name.
    # Params: none.
    def get_budgets(self) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, category, monthly_limit
                FROM budgets
                ORDER BY category
                """
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # This method returns month-to-date spending totals grouped by category.
    # Params: none.
    def get_current_month_spend_by_category(self) -> dict[str, float]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT category, COALESCE(SUM(amount), 0) AS spent
                FROM transactions
                WHERE type = 'expense'
                  AND date >= date('now', 'start of month')
                  AND date < date('now', 'start of month', '+1 month')
                GROUP BY category
                """
            )
            return {row[0]: float(row[1]) for row in cursor.fetchall()}
        finally:
            conn.close()


_db_instance: Optional[FinanceDatabase] = None


# This helper returns one shared FinanceDatabase instance for the app.
# Params: none.
def get_db() -> FinanceDatabase:
    global _db_instance
    if _db_instance is None:
        _db_instance = FinanceDatabase()
    return _db_instance
