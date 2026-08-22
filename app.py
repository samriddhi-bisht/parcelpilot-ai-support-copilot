from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from app.agent.orchestrator import ParcelPilotAgent
from app.config import (
    APP_NAME,
    CUSTOMER_ROLE,
    INTERNAL_ROLE,
    SNAPSHOT_TIME,
)
from app.services.data_service import (
    DataServiceError,
    ParcelPilotDataService,
)
from app.services.document_service import (
    DocumentServiceError,
    ParcelPilotDocumentService,
)
from app.tools.action_tool import EscalationActionTool
from app.tools.support_tools import ParcelPilotSupportTools
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


@st.cache_resource
def load_document_service() -> ParcelPilotDocumentService:
    return ParcelPilotDocumentService()


@st.cache_resource
def load_agent() -> ParcelPilotAgent:
    data_service = load_data_service()
    document_service = load_document_service()
    support_tools = ParcelPilotSupportTools(
        data_service=data_service,
    )
    action_tool = EscalationActionTool(
        data_service=data_service,
    )

    return ParcelPilotAgent(
        support_tools=support_tools,
        document_service=document_service,
        action_tool=action_tool,
    )


def initialise_session_state() -> None:
    defaults = {
        "messages": [],
        "active_role": INTERNAL_ROLE,
        "active_account_id": None,
        "workspace": "Assistant",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_conversation() -> None:
    st.session_state.messages = []


def format_account_option(account: dict[str, Any]) -> str:
    return f"{account['account_name']} - {account['account_id']}"


def render_header() -> None:
    st.markdown(
        """
        <div class="brand-kicker">Operations Intelligence</div>
        <h1 class="brand-title">ParcelPilot Control Desk</h1>
        <div class="brand-description">
            Source-aware assistance for customer support and logistics
            operations.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(
    data_service: ParcelPilotDataService,
) -> tuple[str, str | None, str]:
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">ParcelPilot</div>
        <div class="sidebar-caption">
            Support intelligence workspace
        </div>
        """,
        unsafe_allow_html=True,
    )

    workspace = st.sidebar.radio(
        "Workspace",
        options=["Assistant", "Source Library"],
    )

    role = st.sidebar.selectbox(
        "Access context",
        options=[INTERNAL_ROLE, CUSTOMER_ROLE],
    )

    selected_account_id: str | None = None

    if role == CUSTOMER_ROLE:
        accounts = data_service.list_accounts()

        account_labels = {
            format_account_option(account): account["account_id"]
            for account in accounts
        }

        selected_label = st.sidebar.selectbox(
            "Signed-in account",
            options=list(account_labels.keys()),
        )

        selected_account_id = account_labels[selected_label]

        st.sidebar.markdown(
            """
            <div class="role-note">
                Customer access is restricted in the data and document
                tool layers to the selected account.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            """
            <div class="role-note">
                Internal support access can investigate all supplied
                accounts and prepare controlled operational actions.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.divider()

    if st.sidebar.button(
        "Start new conversation",
        use_container_width=True,
    ):
        reset_conversation()
        st.rerun()

    st.sidebar.caption(
        f"Dataset reference time\n{SNAPSHOT_TIME}"
    )

    previous_role = st.session_state.active_role
    previous_account = st.session_state.active_account_id

    if (
        previous_role != role
        or previous_account != selected_account_id
    ):
        reset_conversation()

    st.session_state.active_role = role
    st.session_state.active_account_id = selected_account_id
    st.session_state.workspace = workspace

    return role, selected_account_id, workspace


def render_context_bar(
    data_service: ParcelPilotDataService,
    role: str,
    account_id: str | None,
) -> None:
    if role == CUSTOMER_ROLE and account_id:
        account = data_service.get_account(account_id)

        if account:
            st.markdown(
                f"""
                <div class="context-bar">
                    Customer workspace:
                    <strong>{account['account_name']}</strong>
                    &nbsp; | &nbsp; {account['account_id']}
                    &nbsp; | &nbsp; {account['plan']} plan
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

    st.markdown(
        """
        <div class="context-bar">
            Internal workspace: authorised support and operations access
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(role: str) -> None:
    if role == CUSTOMER_ROLE:
        examples = [
            "Can I cancel ORD-1001 without a fee?",
            "Is ORD-2002 eligible for a service credit?",
            "Show the details for TKT-501.",
            "What are the current support response targets?",
        ]
    else:
        examples = [
            "Assess the severity and SLA status of TKT-501.",
            "Can Northstar cancel ORD-1001 without a fee?",
            "Escalate TKT-501 because it is a production outage.",
            "What is the workaround for large bulk uploads?",
        ]

    st.markdown(
        '<div class="section-title">Suggested requests</div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(2)

    for index, example in enumerate(examples):
        with columns[index % 2]:
            if st.button(
                example,
                key=f"example_{index}",
                use_container_width=True,
                type="secondary",
            ):
                process_user_message(example)


def render_tool_traces(
    tool_traces: list[dict[str, Any]],
) -> None:
    if not tool_traces:
        return

    with st.expander(
        f"Tool activity ({len(tool_traces)})",
        expanded=False,
    ):
        for index, trace in enumerate(tool_traces, start=1):
            tool_name = trace.get("tool_name", "unknown_tool")
            summary = trace.get("summary", "")
            success = trace.get("success", False)

            status = "Completed" if success else "Could not complete"

            st.markdown(
                f"**{index}. {tool_name}**  \n"
                f"{status}: {summary}"
            )

            data = trace.get("data")

            if data:
                st.json(data, expanded=False)


def render_sources(sources: list[str]) -> None:
    if not sources:
        return

    with st.expander(
        f"Sources used ({len(sources)})",
        expanded=False,
    ):
        for source in sources:
            st.markdown(f"- {source}")


def render_warnings(warnings: list[str]) -> None:
    for warning in warnings:
        st.warning(warning)


def render_confirmation(
    message_index: int,
    pending_action_id: str,
) -> None:
    st.markdown(
        f"""
        <div class="confirmation-panel">
            <div class="confirmation-title">
                Explicit confirmation required
            </div>
            <div class="confirmation-text">
                Action {pending_action_id} is prepared but has not been
                executed.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    confirm_column, cancel_column, spacer = st.columns(
        [1, 1, 3]
    )

    with confirm_column:
        if st.button(
            "Confirm action",
            key=f"confirm_{message_index}_{pending_action_id}",
            use_container_width=True,
        ):
            execute_pending_action(
                pending_action_id=pending_action_id,
                confirmed=True,
            )

    with cancel_column:
        if st.button(
            "Cancel action",
            key=f"cancel_{message_index}_{pending_action_id}",
            use_container_width=True,
            type="secondary",
        ):
            execute_pending_action(
                pending_action_id=pending_action_id,
                confirmed=False,
            )


def render_message(
    message: dict[str, Any],
    message_index: int,
) -> None:
    message_role = message.get("role", "assistant")

    with st.chat_message(message_role):
        st.markdown(message.get("content", ""))

        if message_role != "assistant":
            return

        response = message.get("response", {})

        confidence = response.get("confidence", "medium")
        intent = response.get("intent", "unknown")

        st.markdown(
            f"""
            <div class="answer-meta">
                Confidence: {confidence.title()}
                &nbsp; | &nbsp;
                Route: {intent.replace("_", " ").title()}
            </div>
            """,
            unsafe_allow_html=True,
        )

        render_warnings(response.get("warnings", []))
        render_tool_traces(response.get("tool_traces", []))
        render_sources(response.get("sources", []))

        pending_action_id = response.get("pending_action_id")
        requires_confirmation = response.get(
            "requires_confirmation",
            False,
        )
        action_resolved = message.get(
            "action_resolved",
            False,
        )

        if (
            requires_confirmation
            and pending_action_id
            and not action_resolved
        ):
            render_confirmation(
                message_index=message_index,
                pending_action_id=pending_action_id,
            )


def execute_pending_action(
    pending_action_id: str,
    confirmed: bool,
) -> None:
    agent = load_agent()
    role = st.session_state.active_role
    account_id = st.session_state.active_account_id

    command = (
        f"Confirm {pending_action_id}"
        if confirmed
        else f"Cancel action {pending_action_id}"
    )

    response = agent.handle_message(
        message=command,
        role=role,
        account_id=account_id,
    )

    for message in st.session_state.messages:
        stored_response = message.get("response", {})

        if (
            stored_response.get("pending_action_id")
            == pending_action_id
        ):
            message["action_resolved"] = True

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response.answer,
            "response": response.to_dict(),
        }
    )

    st.rerun()


def process_user_message(message: str) -> None:
    agent = load_agent()
    role = st.session_state.active_role
    account_id = st.session_state.active_account_id

    st.session_state.messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    response = agent.handle_message(
        message=message,
        role=role,
        account_id=account_id,
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response.answer,
            "response": response.to_dict(),
        }
    )

    st.rerun()


def render_assistant_workspace(
    data_service: ParcelPilotDataService,
    role: str,
    account_id: str | None,
) -> None:
    render_context_bar(
        data_service=data_service,
        role=role,
        account_id=account_id,
    )

    if not st.session_state.messages:
        render_empty_state(role)

    for index, message in enumerate(
        st.session_state.messages
    ):
        render_message(
            message=message,
            message_index=index,
        )

    user_message = st.chat_input(
        "Ask about orders, tickets, policies, credits, or escalations"
    )

    if user_message:
        process_user_message(user_message)


def render_source_result(result: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="source-card">
            <div class="source-title">
                {result['title']}
            </div>
            <div class="source-meta">
                {result['authority_label']}
                &nbsp; | &nbsp;
                Status: {result['status'].title()}
                &nbsp; | &nbsp;
                Authority score: {result['authority_rank']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for snippet in result.get("snippets", [])[:2]:
        st.caption(snippet)


def render_source_library(
    document_service: ParcelPilotDocumentService,
    role: str,
    account_id: str | None,
) -> None:
    st.markdown(
        """
        <div class="context-bar">
            Search current policies, signed agreements, operating
            procedures, and product documentation.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Source search</div>',
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "Search sources",
        placeholder=(
            "For example: cancellation fee, support SLA, "
            "late pickup credit"
        ),
        label_visibility="collapsed",
    )

    include_deprecated = False

    if role == INTERNAL_ROLE:
        include_deprecated = st.checkbox(
            "Include deprecated material for audit review",
            value=False,
        )

    if query.strip():
        results = document_service.search(
            query=query,
            account_id=(
                account_id if role == CUSTOMER_ROLE else None
            ),
            include_deprecated=include_deprecated,
            limit=6,
        )

        if not results:
            st.info(
                "No accessible source matched the search."
            )
            return

        st.caption(
            f"{len(results)} accessible source matches"
        )

        for result in results:
            render_source_result(result)
    else:
        documents = document_service.list_documents(
            include_deprecated=include_deprecated
        )

        if role == CUSTOMER_ROLE:
            documents = [
                document
                for document in documents
                if (
                    document.document_type
                    != "customer_agreement"
                    or document.account_id == account_id
                )
            ]

        st.markdown(
            '<div class="section-title">Available sources</div>',
            unsafe_allow_html=True,
        )

        rows = [
            {
                "Source": document.title,
                "Type": document.document_type.replace(
                    "_",
                    " ",
                ).title(),
                "Status": document.status.title(),
                "Authority": document.authority_label,
                "Account scope": (
                    document.account_id or "General"
                ),
            }
            for document in documents
        ]

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )


def main() -> None:
    initialise_session_state()
    render_header()

    try:
        data_service = load_data_service()
        document_service = load_document_service()
        load_agent()
    except (DataServiceError, DocumentServiceError) as exc:
        st.error(str(exc))
        st.stop()

    role, account_id, workspace = render_sidebar(
        data_service=data_service
    )

    if workspace == "Assistant":
        render_assistant_workspace(
            data_service=data_service,
            role=role,
            account_id=account_id,
        )
    else:
        render_source_library(
            document_service=document_service,
            role=role,
            account_id=account_id,
        )


if __name__ == "__main__":
    main()