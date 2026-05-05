"""Main Streamlit entry point: page config, database startup, and sidebar navigation."""

import streamlit as st

from categories import render as render_categories
from budgets import render as render_budgets
from dashboard import render as render_dashboard
from database import get_db
from reports import render as render_reports
from theme import apply_global_styles
from transactions import render as render_transactions

_NAV = (
    ("\U0001f4ca Dashboard", "Dashboard"),
    ("\U0001f4cb Transactions", "Transactions"),
    ("\U0001f3f7\ufe0f Categories", "Categories"),
    ("\U0001f4dd Reports", "Reports"),
    ("\U0001f4b8 Budgets", "Budgets"),
)


def main():
    """
    Configures the app’s browser tab and layout, makes sure SQLite tables exist,
    and switches between the dashboard, transactions, and categories screens.
    """
    st.set_page_config(
        page_title="Personal Finance Tracker",
        page_icon="\U0001f4b0",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_global_styles()
    db = get_db()
    db.init_db()

    st.sidebar.markdown(
        '<p style="font-size:1.15rem;font-weight:700;color:#ffffff;margin:0 0 0.15rem 0;">'
        "Personal Finance"
        "</p>"
        '<p style="font-size:0.8rem;color:#a3a3a3;margin:0 0 1rem 0;line-height:1.4;">'
        "Income, expenses, and categories in one place."
        "</p>",
        unsafe_allow_html=True,
    )
    labels = [label for label, _ in _NAV]
    page_by_label = dict(_NAV)
    choice = st.sidebar.selectbox(
        "Go to page",
        labels,
        label_visibility="collapsed",
    )
    page = page_by_label[choice]
    st.sidebar.divider()
    st.sidebar.caption(
        "Tip: use each page’s date filters to focus on the period you care about."
    )

    if page == "Dashboard":
        render_dashboard()
    elif page == "Transactions":
        render_transactions()
    elif page == "Categories":
        render_categories()
    elif page == "Reports":
        render_reports()
    else:
        render_budgets()


main()
