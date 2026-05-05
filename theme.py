"""Shared look-and-feel: injects CSS and small UI building blocks for every page."""

import html
import streamlit as st

# Colors used in Python (Plotly) and CSS for one unified dark theme.
COLOR_INCOME = "#ffffff"
COLOR_EXPENSE = "#e5e7eb"
COLOR_NET_POSITIVE = "#ffffff"
COLOR_NET_NEGATIVE = "#e5e7eb"
COLOR_MUTED = "#a3a3a3"
COLOR_BORDER = "#262626"


def apply_global_styles():
    """
    Loads one compact stylesheet so the app feels cohesive: spacing, sidebar,
    metrics, buttons, and expanders match across Dashboard, Transactions, and Categories.
    """
    st.markdown(
        f"""
        <style>
            .block-container {{
                padding-top: 2rem;
                padding-bottom: 3rem;
                max-width: 1200px;
            }}
            [data-testid="stSidebar"] {{
                background: #0b0b0c;
                border-right: 1px solid {COLOR_BORDER};
            }}
            [data-testid="stSidebar"] .stSelectbox label {{
                font-weight: 600;
                color: #ffffff;
            }}
            h1 {{
                font-weight: 700 !important;
                letter-spacing: -0.02em;
                /* Use the active theme color so text stays readable on dark backgrounds. */
                color: inherit !important;
            }}
            h2, h3 {{
                font-weight: 600 !important;
                color: inherit !important;
            }}
            div[data-testid="stExpander"] {{
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
                background: #0b0b0c;
                overflow: hidden;
            }}
            div[data-testid="stExpander"] details {{
                border: none;
            }}
            .stButton button {{
                border-radius: 8px;
                font-weight: 600;
            }}
            .finance-kpi {{
                background: #0b0b0c;
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
                padding: 1.2rem 1.35rem;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
                height: 100%;
            }}
            .finance-kpi-label {{
                font-size: 0.72rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: {COLOR_MUTED};
                margin-bottom: 0.4rem;
            }}
            .finance-kpi-value {{
                font-size: 1.55rem;
                font-weight: 700;
                line-height: 1.2;
                letter-spacing: -0.02em;
            }}
            .finance-section-label {{
                font-size: 0.75rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: {COLOR_MUTED};
                margin: 0 0 0.5rem 0;
            }}
            .finance-filter-box {{
                background: #0b0b0c;
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
                padding: 1rem 1.25rem;
                margin-bottom: 1rem;
            }}
            .finance-table-header {{
                font-size: 0.7rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: {COLOR_MUTED};
                padding-bottom: 0.35rem;
                border-bottom: 1px solid {COLOR_BORDER};
                margin-bottom: 0.5rem;
            }}
            .finance-row {{
                padding: 0.45rem 0;
                border-bottom: 1px solid {COLOR_BORDER};
                font-size: 0.95rem;
            }}
            .finance-type-pill {{
                display: inline-block;
                padding: 0.2rem 0.55rem;
                border-radius: 6px;
                font-size: 0.78rem;
                font-weight: 700;
            }}
            .pill-income {{
                background: #111113;
                color: #ffffff;
            }}
            .pill-expense {{
                background: #111113;
                color: #ffffff;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(title: str, value: str, accent: str):
    """
    Draws one summary tile (title + big number) with a color accent key:
    income, expense, net_pos, or net_neg.
    """
    colors = {
        "income": COLOR_INCOME,
        "expense": COLOR_EXPENSE,
        "net_pos": COLOR_NET_POSITIVE,
        "net_neg": COLOR_NET_NEGATIVE,
    }
    color = colors.get(accent, "#334155")
    safe_title = html.escape(title)
    safe_value = html.escape(value)
    st.markdown(
        f'<div class="finance-kpi"><div class="finance-kpi-label">{safe_title}</div>'
        f'<div class="finance-kpi-value" style="color:{color};">{safe_value}</div></div>',
        unsafe_allow_html=True,
    )


def type_pill_html(txn_type: str) -> str:
    """
    Returns a short HTML snippet that styles income vs expense as a colored pill.
    """
    t = (txn_type or "").lower()
    if t == "income":
        cls = "finance-type-pill pill-income"
    else:
        cls = "finance-type-pill pill-expense"
    label = html.escape(txn_type or "")
    return f'<span class="{cls}">{label}</span>'
