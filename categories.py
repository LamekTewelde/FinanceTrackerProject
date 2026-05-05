"""Categories page: list, create, and remove unused category labels."""

import html
import sqlite3

import streamlit as st

from database import get_db
from theme import type_pill_html


def render():
    """
    Lists every category, offers a small form to create new name+type pairs,
    and shows delete buttons only when no transactions reference that label.
    """
    st.title("Categories")
    st.caption(
        "Group your spending and income. You can only delete a label after nothing uses it."
    )

    db = get_db()
    rows = db.get_categories()

    with st.container(border=True):
        st.markdown(
            '<p class="finance-section-label" style="margin:0 0 0.5rem 0;">New category</p>',
            unsafe_allow_html=True,
        )
        with st.form("add_category_form", clear_on_submit=True):
            c1, c2 = st.columns(2, gap="medium")
            with c1:
                name_in = st.text_input(
                    "Name",
                    placeholder="e.g. Subscriptions, Pet care…",
                )
            with c2:
                type_in = st.selectbox("Type", ["expense", "income"], key="new_cat_type")
            submitted = st.form_submit_button("Add category", type="primary")
            if submitted:
                if not name_in or not name_in.strip():
                    st.error("Name cannot be empty.")
                else:
                    try:
                        db.add_category(name_in.strip(), type_in)
                        st.success("Category added.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("That name and type combination already exists.")

    st.divider()
    st.markdown("##### Your categories")
    if not rows:
        st.info("No categories yet — add one in the box above.")
        return

    st.caption(f"{len(rows)} label(s) · “In use” means at least one transaction references it.")

    h1, h2, h3, h4 = st.columns([0.55, 2.1, 1.05, 0.95])
    h1.markdown('<div class="finance-table-header">ID</div>', unsafe_allow_html=True)
    h2.markdown('<div class="finance-table-header">Name</div>', unsafe_allow_html=True)
    h3.markdown('<div class="finance-table-header">Type</div>', unsafe_allow_html=True)
    h4.markdown('<div class="finance-table-header"> </div>', unsafe_allow_html=True)

    for c in rows:
        used = db.count_transactions_for_category(c["name"], c["type"]) > 0
        r1, r2, r3, r4 = st.columns([0.55, 2.1, 1.05, 0.95])
        with r1:
            st.markdown(
                f'<div class="finance-row">{html.escape(str(c["id"]))}</div>',
                unsafe_allow_html=True,
            )
        with r2:
            st.markdown(
                f'<div class="finance-row">{html.escape(str(c["name"]))}</div>',
                unsafe_allow_html=True,
            )
        with r3:
            st.markdown(type_pill_html(c["type"]), unsafe_allow_html=True)
        with r4:
            if used:
                st.caption("In use")
            else:
                if st.button("Delete", key=f"del_cat_{c['id']}", type="secondary"):
                    ok = db.delete_category(int(c["id"]))
                    if ok:
                        st.success("Category removed.")
                        st.rerun()
                    else:
                        st.error("Could not delete — it may now be tied to transactions.")
