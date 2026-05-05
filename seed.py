"""
Run once to create tables and fill the database with about three months of sample data.
Usage: python seed.py
"""

import random
import sqlite3
from datetime import date, timedelta

from database import (
    DB_PATH,
    get_db,
)


def _days_in_last_n_months(n_months: int, end_day: date) -> list[date]:
    """
    Builds a list of calendar dates covering roughly the last n_months ending on end_day,
    one date per day for seeding variety (not every day will get a transaction).
    """
    start = end_day - timedelta(days=30 * n_months)
    out = []
    d = start
    while d <= end_day:
        out.append(d)
        d += timedelta(days=1)
    return out


def seed_categories(db):
    """
    Ensures expense and income categories exist in the database,
    skipping inserts that would violate the unique name+type rule.
    """
    expense_names = [
        "Rent",
        "Groceries",
        "Transport",
        "Dining",
        "Entertainment",
        "Utilities",
    ]
    income_names = ["Salary", "Freelance"]
    for name in expense_names:
        try:
            db.add_category(name, "expense")
        except sqlite3.IntegrityError:
            pass
    for name in income_names:
        try:
            db.add_category(name, "income")
        except sqlite3.IntegrityError:
            pass


def seed_transactions(db, rng: random.Random):
    """
    Inserts realistic-looking income and expense rows across ~3 months
    using fixed templates so totals look plausible for demos.
    """
    end = date.today()
    days = _days_in_last_n_months(3, end)

    # Salary: twice per month (approx)
    salary_days = sorted(rng.sample(days, k=min(6, len(days))))
    for d in salary_days[:6]:
        db.add_transaction(
            round(rng.uniform(3200, 3800), 2),
            "income",
            "Salary",
            d.isoformat(),
            "Payroll deposit",
        )

    # Freelance: sporadic
    for _ in range(rng.randint(4, 9)):
        d = rng.choice(days)
        db.add_transaction(
            round(rng.uniform(200, 1200), 2),
            "income",
            "Freelance",
            d.isoformat(),
            rng.choice(["Client invoice", "Side project", "Consulting"]),
        )

    # Rent: once per month (same-ish day)
    month_starts = sorted({date(d.year, d.month, min(3, d.day)) for d in days})
    for m in sorted(month_starts)[-3:]:
        db.add_transaction(
            1850.0,
            "expense",
            "Rent",
            m.isoformat(),
            "Monthly rent",
        )

    templates = [
        ("Groceries", 35, 180),
        ("Transport", 15, 120),
        ("Dining", 25, 200),
        ("Entertainment", 10, 150),
        ("Utilities", 60, 220),
    ]

    for d in days:
        if rng.random() < 0.35:
            cat, lo, hi = rng.choice(templates)
            db.add_transaction(
                round(rng.uniform(lo, hi), 2),
                "expense",
                cat,
                d.isoformat(),
                "",
            )
        if rng.random() < 0.12:
            db.add_transaction(
                round(rng.uniform(40, 95), 2),
                "expense",
                "Groceries",
                d.isoformat(),
                "Quick shop",
            )


def main():
    """
    Wipes and recreates a fresh seeded database, then prints a success message.
    """
    if DB_PATH.exists():
        DB_PATH.unlink()
    db = get_db()
    db.init_db()
    seed_categories(db)
    seed_transactions(db, random.Random(42))
    # Sanity check: DB responds
    _ = db.get_summary("2000-01-01", "2099-12-31")
    _ = db.get_expense_totals_by_category("2000-01-01", "2099-12-31")
    _ = db.get_categories()
    print("Database seeded successfully!")


if __name__ == "__main__":
    main()
