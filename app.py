from __future__ import annotations

import pandas as pd
import streamlit as st

from app.config import (
    APP_NAME,
    APP_TAGLINE,
    CUSTOMER_ROLE,
    INTERNAL_ROLE,
    SNAPSHOT_TIME,
)
from app.services.data_service import (
    DataServiceError,
    ParcelPilotDataService,
)
from app.ui.styles import apply_styles


st.set_page_config(
    page_title=APP_NAME,
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()


@st.cache_resource
def load_data_service() -> ParcelPilotDataService:
    return ParcelPilotDataService()


def format_account_option(account: dict) -> str:
    return f"{account['account_name']} ï¿½ {account['account_id']}"


def render_header() -> None:
    st.markdown(
        """
        <div class="brand-kicker">Operations Intelligence</div>
        <h1 class="brand-title">ParcelPilot Control Desk</h1>
        <div class="brand-description">
            A source-aware workspace for customer support and logistics operations.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(
    service: ParcelPilotDataService,
) -> tuple[str, str]:
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">ParcelPilot</div>
        <div class="sidebar-caption">
            Support intelligence workspace
        </div>
        """,
        unsafe_allow_html=True,
    )

    role = st.sidebar.selectbox(
        "Workspace",
        options=[INTERNAL_ROLE, CUSTOMER_ROLE],
    )

    accounts = service.list_accounts()

    selected_account_id = ""

    if role == CUSTOMER_ROLE:
        account_labels = {
            format_account_option(account): account["account_id"]
            for account in accounts
        }

        selected_label = st.sidebar.selectbox(
            "Signed-in account",
            options=list(account_labels.keys()),
        )

        selected_account_id = account_labels[selected_label]
    else:
        st.sidebar.markdown(
            """
            <div style="
                color:#AFBDCB;
                font-size:0.79rem;
                margin-top:0.8rem;
                line-height:1.5;
            ">
                Internal access can investigate all supplied accounts.
                Customer access is restricted to the selected account.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.divider()

    st.sidebar.caption(f"Dataset snapshot\n{SNAPSHOT_TIME}")

    return role, selected_account_id


def render_metrics(service: ParcelPilotDataService) -> None:
    metrics = service.overview_metrics()

    columns = st.columns(4)

    columns[0].metric("Active accounts", metrics["active_accounts"])
    columns[1].metric("Orders in snapshot", metrics["orders"])
    columns[2].metric("Open tickets", metrics["open_tickets"])
    columns[3].metric("Carrier partners", metrics["carriers"])


def render_customer_workspace(
    service: ParcelPilotDataService,
    account_id: str,
) -> None:
    account = service.get_account(account_id)

    if not account:
        st.error("The selected account could not be found.")
        return

    st.markdown(
        f"""
        <div class="context-bar">
            Customer context: <strong>{account['account_name']}</strong>
            &nbsp;ï¿½&nbsp; {account['account_id']}
            &nbsp;ï¿½&nbsp; {account['plan']} plan
        </div>
        """,
        unsafe_allow_html=True,
    )

    account_columns = st.columns(3)
    account_columns[0].metric("Plan", account["plan"])
    account_columns[1].metric("Customer success manager", account["csm"])
    account_columns[2].metric(
        "Premium support",
        "Included" if bool(account["premium_support"]) else "Not included",
    )

    st.markdown(
        '<div class="section-title">Order lookup</div>',
        unsafe_allow_html=True,
    )

    lookup_column, button_column = st.columns([4, 1])

    with lookup_column:
        order_id = st.text_input(
            "Order ID",
            placeholder="Enter an order ID such as ORD-1001",
            label_visibility="collapsed",
        )

    with button_column:
        lookup_order = st.button(
            "Find order",
            use_container_width=True,
        )

    if lookup_order:
        if not order_id.strip():
            st.warning("Enter an order ID.")
        else:
            order = service.get_order(
                order_id=order_id,
                permitted_account_id=account_id,
            )

            if order:
                result = pd.DataFrame([order])
                st.dataframe(
                    result,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.error(
                    "No matching order is available for this account."
                )

    st.markdown(
        '<div class="section-title">Account activity</div>',
        unsafe_allow_html=True,
    )

    orders_tab, tickets_tab = st.tabs(
        ["Orders", "Support tickets"]
    )

    with orders_tab:
        orders = service.get_account_orders(account_id)
        st.dataframe(
            orders,
            use_container_width=True,
            hide_index=True,
        )

    with tickets_tab:
        tickets = service.get_account_tickets(account_id)
        st.dataframe(
            tickets,
            use_container_width=True,
            hide_index=True,
        )


def render_internal_workspace(
    service: ParcelPilotDataService,
) -> None:
    st.markdown(
        """
        <div class="context-bar">
            Internal workspace: authorised support and operations access
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_metrics(service)

    st.markdown(
        '<div class="section-title">Operational dataset</div>',
        unsafe_allow_html=True,
    )

    accounts_tab, orders_tab, tickets_tab = st.tabs(
        ["Accounts", "Orders", "Tickets"]
    )

    with accounts_tab:
        st.dataframe(
            service.accounts,
            use_container_width=True,
            hide_index=True,
        )

    with orders_tab:
        st.dataframe(
            service.orders,
            use_container_width=True,
            hide_index=True,
        )

    with tickets_tab:
        tickets = service.tickets.copy()

        visible_columns = [
            column
            for column in tickets.columns
            if column != "historical_resolution"
        ]

        st.dataframe(
            tickets[visible_columns],
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Historical resolutions are intentionally excluded from the "
            "primary view because they are non-authoritative context."
        )


def main() -> None:
    render_header()

    try:
        service = load_data_service()
    except DataServiceError as exc:
        st.error(str(exc))
        st.info(
            "Place the supplied ParcelPilot Excel workbook inside "
            "the data folder, then reload the application."
        )
        st.stop()

    role, account_id = render_sidebar(service)

    if role == CUSTOMER_ROLE:
        render_customer_workspace(service, account_id)
    else:
        render_internal_workspace(service)


if __name__ == "__main__":
    main()
