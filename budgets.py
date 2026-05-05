"""Budgets page: set monthly category limits and track current usage."""

import streamlit as st

from database import get_db


# This function returns status metadata for budget usage thresholds.
# Params: ratio (spent divided by limit as a float).
def _budget_status(ratio: float) -> tuple[str, str, str]:
    if ratio > 0.9:
        return "Over 90%", "red", "RED"
    if ratio > 0.7:
        return "Over 70%", "orange", "YELLOW"
    return "Healthy", "green", "GREEN"


# This function renders the budgets page with limit entry and current-month progress.
# Params: none.
def render():
    db = get_db()
    st.title("Budgets")
    st.caption("Set monthly spending caps for expense categories and track this month's progress.")

    expense_categories = db.get_category_names("expense")
    with st.container(border=True):
        st.markdown("##### Set monthly limit")
        if not expense_categories:
            st.warning("Add expense categories first, then you can set budgets here.")
        else:
            with st.form("set_budget_form", clear_on_submit=False):
                c1, c2 = st.columns(2)
                with c1:
                    category = st.selectbox("Category", expense_categories, key="budget_category")
                with c2:
                    monthly_limit = st.number_input(
                        "Monthly limit",
                        min_value=1.0,
                        step=10.0,
                        value=500.0,
                        format="%.2f",
                    )
                submitted = st.form_submit_button("Save budget", type="primary")
                if submitted:
                    db.upsert_budget(category, float(monthly_limit))
                    st.success(f"Saved budget for {category}.")
                    st.rerun()

    st.divider()
    st.markdown("##### Current month progress")
    budgets = db.get_budgets()
    month_spend = db.get_current_month_spend_by_category()

    if not budgets:
        st.info("No budgets configured yet.")
        return

    over_budget = []
    for budget in budgets:
        category = budget["category"]
        limit_amount = float(budget["monthly_limit"])
        spent = month_spend.get(category, 0.0)
        ratio = 0.0 if limit_amount <= 0 else spent / limit_amount
        progress_value = min(ratio, 1.0)
        status_label, color_name, signal = _budget_status(ratio)

        st.markdown(f"**{category}**  \nSpent ${spent:,.2f} of ${limit_amount:,.2f} ({ratio*100:.1f}%)")
        st.progress(progress_value, text=f"{status_label} • {signal}")
        st.markdown(
            f"<div style='height:8px;border-radius:999px;background:#222;overflow:hidden;'>"
            f"<div style='height:8px;width:{min(ratio*100,100):.2f}%;background:{color_name};'></div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.caption("Color legend: green < 70%, yellow > 70%, red > 90%.")
        st.write("")
        if ratio > 1:
            over_budget.append(category)

    if over_budget:
        st.warning("Over budget this month: " + ", ".join(over_budget))
