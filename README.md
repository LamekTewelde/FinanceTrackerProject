# Personal Finance Tracker

A personal finance web app built with Python and Streamlit. Track income and expenses, set monthly budgets, organize transactions by category, and visualize spending trends, all running locally in your browser.
## Features

- Add and delete income/expense transactions with date, category, and notes
- Custom categories for both income and expenses
- Monthly budget limits per category with real-time tracking
- Dashboard with summary KPIs (total income, expenses, net balance)
- Plotly charts: spending donut, monthly income vs expense bar chart
- Date range filters across all pages
- Reports page for deeper spending breakdowns
- SQLite database — no external services needed

## Tech Stack

- **Python** — core application logic
- **Streamlit** — browser-based UI
- **SQLite** — local data storage
- **Plotly** — interactive charts
- **Pandas** — data manipulation
## Install

```bash
pip install -r requirements.txt
```

## Seed sample data (optional)

Creates the database and fills roughly three months of realistic sample transactions for a demo:

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
| `seed.py` | Demo data generator |
