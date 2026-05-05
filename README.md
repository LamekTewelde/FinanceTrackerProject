# Personal Finance Tracker

This project is a small **personal finance tracker** you run in the browser. It lets you record income and expenses, organize them with categories, and view simple charts and totals.

Everything is implemented in **Python** using Streamlit for the UI, SQLite for storage, and Plotly plus Pandas for charts and tables.

## Install

```bash
pip install -r requirements.txt
```

## Seed sample data

Creates the database and fills roughly three months of realistic sample transactions (run once, or anytime you want a fresh demo database):

```bash
python seed.py
```

## Run the app

```bash
streamlit run app.py
```

## Files

| File | Role |
|------|------|
| `app.py` | Streamlit entry point: page title/icon, sidebar navigation, loads the chosen screen. |
| `theme.py` | Shared UI polish: global CSS plus small helpers (KPI cards, type “pills”). |
| `database.py` | All SQLite code: create tables, insert/delete/query transactions and categories. |
| `dashboard.py` | Summary metrics (income, expenses, net balance) and Plotly donut/bar charts with a date filter. |
| `transactions.py` | Filterable transaction list, add form in an expander, and per-row delete buttons. |
| `categories.py` | List categories, add new ones, delete only when no transactions use them. |
| `seed.py` | Wipes `finance.db`, recreates schema, and inserts sample income/expense rows. |
| `requirements.txt` | Python dependencies: Streamlit, Plotly, Pandas. |
