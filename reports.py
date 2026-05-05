"""Reports page: advanced SQL examples rendered in Streamlit."""

import sqlite3
from pathlib import Path
from typing import Any, Optional

import streamlit as st

from database import get_db


# This function runs one SQL query using sqlite3 and returns rows as dictionaries.
# Params: db_path (Path to SQLite file), sql (query text), params (optional tuple values).
def _run_query(db_path: Path, sql: str, params: Optional[tuple[Any, ...]] = None) -> list[dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


# This function renders one report section with title, table output, and raw SQL expander.
# Params: title (section heading), db_path (Path to DB), sql (query text), params (optional tuple values).
def _render_sql_report(title: str, db_path: Path, sql: str, params: Optional[tuple[Any, ...]] = None):
    st.markdown(f"#### {title}")
    rows = _run_query(db_path, sql, params)
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No rows returned for this report.")
    with st.expander("Show raw SQL"):
        st.code(sql.strip(), language="sql")


# This function renders the full reports page with five advanced SQL examples.
# Params: none.
def render():
    db = get_db()
    st.title("Reports")
    st.caption("These reports use direct sqlite3 queries and display the SQL under each result.")

    sql_top_5 = """
    SELECT category,
           ROUND(SUM(amount), 2) AS total_spent
    FROM transactions
    WHERE type = 'expense'
      AND date >= date('now', 'start of month')
      AND date < date('now', 'start of month', '+1 month')
    GROUP BY category
    ORDER BY total_spent DESC
    LIMIT 5;
    """
    _render_sql_report("1) Top 5 spending categories this month", db.db_path, sql_top_5)

    sql_avg_daily = """
    SELECT ROUND(COALESCE(SUM(amount), 0) / 30.0, 2) AS average_daily_spending
    FROM transactions
    WHERE type = 'expense'
      AND date >= date('now', '-29 days')
      AND date <= date('now');
    """
    _render_sql_report("2) Average daily spending (last 30 days)", db.db_path, sql_avg_daily)

    sql_highest_month = """
    SELECT strftime('%Y-%m', date) AS month,
           ROUND(SUM(amount), 2) AS total_expense
    FROM transactions
    WHERE type = 'expense'
      AND date >= date('now', '-12 months')
    GROUP BY month
    ORDER BY total_expense DESC
    LIMIT 1;
    """
    _render_sql_report("3) Month with highest expenses (last 12 months)", db.db_path, sql_highest_month)

    sql_ratio = """
    SELECT strftime('%Y-%m', date) AS month,
           ROUND(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 2) AS income,
           ROUND(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 2) AS expense,
           ROUND(
               CASE
                   WHEN SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) = 0 THEN NULL
                   ELSE SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END)
                        / SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END)
               END,
               2
           ) AS income_expense_ratio
    FROM transactions
    WHERE date >= date('now', '-6 months')
    GROUP BY month
    ORDER BY month;
    """
    _render_sql_report("4) Income vs expense ratio by month (last 6 months)", db.db_path, sql_ratio)

    sql_biggest_per_category = """
    SELECT t.category,
           ROUND(t.amount, 2) AS biggest_transaction,
           t.type,
           t.date,
           COALESCE(t.note, '') AS note
    FROM transactions t
    INNER JOIN (
        SELECT category, MAX(amount) AS max_amount
        FROM transactions
        GROUP BY category
    ) mx ON mx.category = t.category AND mx.max_amount = t.amount
    ORDER BY t.category, t.amount DESC;
    """
    _render_sql_report("5) Biggest single transaction per category", db.db_path, sql_biggest_per_category)
