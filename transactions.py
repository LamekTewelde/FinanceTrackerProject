"""Transactions page: browse, filter, add, and remove entries."""

import html
import io
import csv
from datetime import date

import streamlit as st

from database import get_db
from theme import type_pill_html


def _category_filter_options(db):
    """
    Builds the list used in the category filter dropdown: an “All” option plus every name.
    """
    cats = db.get_categories()
    names = sorted({c["name"] for c in cats})
    return ["All"] + names


def render():
    """
    Shows the filterable transaction table, per-row delete actions,
    and an expander with a type picker plus a form to add new rows.
    """
    db = get_db()
    st.title("Transactions")
    st.caption("Filter the list, add new entries, or remove mistakes—newest rows appear first.")

    with st.container(border=True):
        st.markdown(
            '<p class="finance-section-label" style="margin:0 0 0.5rem 0;">Filters</p>',
            unsafe_allow_html=True,
        )
        filter_col1, filter_col2, filter_col3 = st.columns(3, gap="medium")
        with filter_col1:
            type_choice = st.selectbox(
                "Type",
                ["All", "income", "expense"],
                key="tx_filter_type",
            )
        with filter_col2:
            cat_choice = st.selectbox(
                "Category",
                _category_filter_options(db),
                key="tx_filter_cat",
            )
        with filter_col3:
            dr = st.date_input(
                "Posted between",
                value=(date.today().replace(day=1), date.today()),
                key="tx_filter_dates",
            )

    if isinstance(dr, tuple) and len(dr) == 2:
        d0, d1 = dr
    elif isinstance(dr, date):
        d0 = d1 = dr
    else:
        st.warning("Pick a date or a start/end pair for filtering.")
        d0 = d1 = date.today()

    if d0 > d1:
        st.error("Start date must be on or before the end date.")
        return

    type_param = None if type_choice == "All" else type_choice
    cat_param = None if cat_choice == "All" else cat_choice

    rows = db.get_transactions(
        {
            "type": type_param,
            "category": cat_param,
            "date_start": d0.isoformat(),
            "date_end": d1.isoformat(),
        }
    )

    with st.expander("Add a new transaction", expanded=False):
        all_cats = db.get_categories()
        if not all_cats:
            st.error("Add at least one category before recording transactions.")
        else:
            # Type must live outside st.form(): widgets inside a form do not rerun the script
            # until you submit, so the category dropdown would stay on the old list.
            add_type = st.selectbox(
                "Type",
                ["expense", "income"],
                key="add_tx_type",
            )
            names = db.get_category_names(add_type)
            if not names:
                st.warning(
                    f"No categories for type “{add_type}”. Add one in Categories."
                )

            with st.form("add_transaction_form", clear_on_submit=True):
                row_a, row_b = st.columns(2, gap="medium")
                with row_a:
                    amount_in = st.number_input(
                        "Amount",
                        min_value=0.01,
                        value=25.0,
                        step=0.01,
                        format="%.2f",
                    )
                with row_b:
                    if names:
                        cat_pick = st.selectbox(
                            "Category",
                            names,
                            key=f"add_tx_cat_{add_type}",
                        )
                    else:
                        st.caption("Add categories for this type first.")
                        cat_pick = None
                add_date = st.date_input("Date", value=date.today(), key="add_tx_date")
                note = st.text_area(
                    "Note (optional)",
                    key="add_tx_note",
                    placeholder="e.g. Weekly shop, invoice #104…",
                    height=68,
                )
                submitted = st.form_submit_button("Save transaction", type="primary")
                if submitted:
                    if cat_pick is None:
                        st.error("Pick a valid category.")
                    else:
                        db.add_transaction(
                            float(amount_in),
                            add_type,
                            cat_pick,
                            add_date.isoformat(),
                            note,
                        )
                        st.success("Transaction saved.")
                        st.rerun()

    st.divider()
    st.markdown("##### Export data")
    b_start, b_end = db.get_transaction_date_bounds()
    if b_start and b_end:
        default_export_start = date.fromisoformat(b_start)
        default_export_end = date.fromisoformat(b_end)
    else:
        default_export_start = date.today().replace(day=1)
        default_export_end = date.today()

    export_range = st.date_input(
        "Export date range",
        value=(default_export_start, default_export_end),
        key="tx_export_range",
    )
    if isinstance(export_range, tuple) and len(export_range) == 2:
        export_start, export_end = export_range
    elif isinstance(export_range, date):
        export_start = export_end = export_range
    else:
        export_start = default_export_start
        export_end = default_export_end

    export_rows = db.get_transactions(
        {
            "date_start": export_start.isoformat(),
            "date_end": export_end.isoformat(),
        }
    )
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["id", "amount", "type", "category", "date", "note"])
    for row in export_rows:
        writer.writerow(
            [row["id"], row["amount"], row["type"], row["category"], row["date"], row.get("note") or ""]
        )
    filename = f"transactions_{export_start.isoformat()}_to_{export_end.isoformat()}.csv"
    st.download_button(
        "Download transactions CSV",
        data=csv_buffer.getvalue(),
        file_name=filename,
        mime="text/csv",
        use_container_width=False,
    )

    st.divider()
    st.markdown("##### Ledger")
    st.caption(f"{len(rows)} row(s) match your filters · sorted newest first")

    if not rows:
        st.info("No transactions match these filters. Try widening the date range or choosing “All”.")
        return

    h1, h2, h3, h4, h5, h6 = st.columns([1.15, 0.95, 1.15, 1.05, 2.0, 0.75])
    h1.markdown('<div class="finance-table-header">Date</div>', unsafe_allow_html=True)
    h2.markdown('<div class="finance-table-header">Type</div>', unsafe_allow_html=True)
    h3.markdown('<div class="finance-table-header">Category</div>', unsafe_allow_html=True)
    h4.markdown('<div class="finance-table-header">Amount</div>', unsafe_allow_html=True)
    h5.markdown('<div class="finance-table-header">Note</div>', unsafe_allow_html=True)
    h6.markdown('<div class="finance-table-header"> </div>', unsafe_allow_html=True)

    for t in rows:
        c1, c2, c3, c4, c5, c6 = st.columns([1.15, 0.95, 1.15, 1.05, 2.0, 0.75])
        with c1:
            st.markdown(
                f'<div class="finance-row">{html.escape(str(t["date"]))}</div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(type_pill_html(t["type"]), unsafe_allow_html=True)
        with c3:
            st.markdown(
                f'<div class="finance-row">{html.escape(str(t["category"]))}</div>',
                unsafe_allow_html=True,
            )
        with c4:
            amt = t["amount"]
            color = "#ffffff" if t["type"] == "income" else "#e5e7eb"
            st.markdown(
                f'<div class="finance-row" style="font-weight:600;color:{color};">'
                f"${amt:,.2f}</div>",
                unsafe_allow_html=True,
            )
        with c5:
            raw_note = (t.get("note") or "").strip()
            note_html = html.escape(raw_note) if raw_note else "—"
            st.markdown(
                f'<div class="finance-row" style="color:#a3a3a3;">{note_html}</div>',
                unsafe_allow_html=True,
            )
        with c6:
            if st.button("Delete", key=f"del_tx_{t['id']}", type="secondary"):
                db.delete_transaction(int(t["id"]))
                st.success("Deleted.")
                st.rerun()
