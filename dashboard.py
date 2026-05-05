"""Dashboard page: filters, summary metrics, and Plotly charts."""

from datetime import date, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from database import get_db
from theme import (
    COLOR_BORDER,
    COLOR_EXPENSE,
    COLOR_INCOME,
    render_kpi_card,
)


def _default_date_range(db):
    """
    Picks sensible start and end dates for the dashboard filter:
    the full span of stored transactions, or the current month if the DB is empty.
    """
    min_s, max_s = db.get_transaction_date_bounds()
    today = date.today()
    if min_s and max_s:
        start = datetime.strptime(min_s, "%Y-%m-%d").date()
        end = datetime.strptime(max_s, "%Y-%m-%d").date()
        return start, end
    first = today.replace(day=1)
    return first, today


def _format_currency(value: float) -> str:
    """
    Turns a numeric amount into a short USD-style string for metrics and labels.
    """
    return f"${value:,.2f}"


def _chart_layout_kwargs():
    """
    Returns shared Plotly layout options so both charts share fonts, margins, and background.
    """
    return dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0b0b0c",
        font=dict(
            family="system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
            size=13,
            color="#ffffff",
        ),
        title=dict(font=dict(size=15, color="#ffffff")),
        margin=dict(t=48, b=48, l=56, r=24),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )


def render():
    """
    Renders the full dashboard: date range picker, three headline numbers,
    expense donut chart, and grouped monthly income vs expense bars.
    """
    st.title("Dashboard")
    st.caption(
        "Pick a period below. Every number and chart updates to match that window."
    )

    db = get_db()
    d_start, d_end = _default_date_range(db)
    with st.container(border=True):
        st.markdown(
            '<p class="finance-section-label" style="margin:0 0 0.35rem 0;">Reporting period</p>',
            unsafe_allow_html=True,
        )
        picked = st.date_input(
            "Date range",
            value=(d_start, d_end),
            label_visibility="collapsed",
            help="Totals and charts include every transaction from the start date "
            "through the end date, inclusive.",
        )

    if isinstance(picked, tuple) and len(picked) == 2:
        range_start, range_end = picked
    elif isinstance(picked, date):
        range_start = range_end = picked
    else:
        st.warning("Choose a start and end date.")
        return

    if range_start > range_end:
        st.error("Start date must be on or before the end date.")
        return

    ds = range_start.isoformat()
    de = range_end.isoformat()

    summary = db.get_summary(ds, de)
    income = summary["income"]
    expense = summary["expense"]
    net = summary["net"]

    st.markdown(
        '<p class="finance-section-label" style="margin-top:1.25rem;">Overview</p>',
        unsafe_allow_html=True,
    )
    k1, k2, k3 = st.columns(3)
    with k1:
        render_kpi_card("Total income", _format_currency(income), "income")
    with k2:
        render_kpi_card("Total expenses", _format_currency(expense), "expense")
    with k3:
        render_kpi_card(
            "Net balance",
            _format_currency(net),
            "net_pos" if net >= 0 else "net_neg",
        )

    spend_rows = db.get_expense_totals_by_category(ds, de)
    month_rows = db.get_monthly_trends_for_range(ds, de)

    st.divider()
    chart_col1, chart_col2 = st.columns(2, gap="large")

    with chart_col1:
        st.markdown("##### Where your money went")
        st.caption("Expense totals split by category.")
        if not spend_rows:
            st.info("No expenses in this range. Add expense transactions to see this chart.")
        else:
            df_donut = pd.DataFrame(spend_rows, columns=["category", "total"])
            fig_donut = px.pie(
                df_donut,
                names="category",
                values="total",
                hole=0.5,
                title="",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig_donut.update_traces(
                textposition="inside",
                textinfo="percent+label",
                marker=dict(line=dict(color="#ffffff", width=1.5)),
            )
            fig_donut.update_layout(
                **_chart_layout_kwargs(),
                showlegend=False,
                height=400,
            )
            st.plotly_chart(fig_donut, width="stretch")

    with chart_col2:
        st.markdown("##### Cash in vs cash out")
        st.caption("Each month inside your selected period.")
        if not month_rows:
            st.info("No transactions in this range yet.")
        else:
            df_bar = pd.DataFrame(
                month_rows, columns=["month", "income", "expense"]
            )
            df_long = df_bar.melt(
                id_vars="month",
                var_name="kind",
                value_name="amount",
            )
            df_long["kind"] = df_long["kind"].str.capitalize()
            fig_bar = px.bar(
                df_long,
                x="month",
                y="amount",
                color="kind",
                barmode="group",
                title="",
                labels={"month": "Month", "amount": "Amount ($)", "kind": ""},
                color_discrete_map={"Income": COLOR_INCOME, "Expense": COLOR_EXPENSE},
            )
            fig_bar.update_layout(
                **_chart_layout_kwargs(),
                legend_title_text="",
                height=400,
                xaxis=dict(showgrid=False, linecolor=COLOR_BORDER),
                yaxis=dict(gridcolor="#f1f5f9", linecolor=COLOR_BORDER),
            )
            st.plotly_chart(fig_bar, width="stretch")
