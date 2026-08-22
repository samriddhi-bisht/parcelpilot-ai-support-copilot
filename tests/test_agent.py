from pathlib import Path

from app.agent.orchestrator import ParcelPilotAgent
from app.tools.action_tool import EscalationActionTool


def test_agent_routes_northstar_cancellation() -> None:
    agent = ParcelPilotAgent()

    response = agent.handle_message(
        message=(
            "Can Northstar cancel ORD-1001 without a "
            "cancellation fee? Explain why."
        ),
        role="Customer",
        account_id="ACCT-001",
    )

    assert response.success is True
    assert response.intent == "cancellation_decision"
    assert response.structured_data["fee_inr"] == 0
    assert response.structured_data["contract_override"] is True


def test_agent_blocks_cross_account_order() -> None:
    agent = ParcelPilotAgent()

    response = agent.handle_message(
        message="Can I cancel ORD-1001?",
        role="Customer",
        account_id="ACCT-002",
    )

    assert response.success is False


def test_agent_routes_service_credit_request() -> None:
    agent = ParcelPilotAgent()

    response = agent.handle_message(
        message="Is ORD-2002 eligible for a service credit?",
        role="Customer",
        account_id="ACCT-002",
    )

    assert response.success is True
    assert response.intent == "service_credit_decision"
    assert response.structured_data["credit_amount_inr"] == 300.0


def test_agent_routes_ticket_assessment() -> None:
    agent = ParcelPilotAgent()

    response = agent.handle_message(
        message="Assess the severity and SLA status of TKT-501.",
        role="Support Operations",
    )

    assert response.success is True
    assert response.intent == "ticket_assessment"
    assert response.structured_data["severity"] == "P1"


def test_customer_cannot_create_escalation() -> None:
    agent = ParcelPilotAgent()

    response = agent.handle_message(
        message="Escalate TKT-501.",
        role="Customer",
        account_id="ACCT-001",
    )

    assert response.success is False
    assert response.intent == "escalation_not_authorised"


def test_internal_agent_prepares_and_confirms_escalation(
    tmp_path: Path,
) -> None:
    action_tool = EscalationActionTool(actions_dir=tmp_path)
    agent = ParcelPilotAgent(action_tool=action_tool)

    prepared = agent.handle_message(
        message="Escalate TKT-501 because it is a production outage.",
        role="Support Operations",
    )

    assert prepared.success is True
    assert prepared.requires_confirmation is True
    assert prepared.pending_action_id is not None

    confirmed = agent.handle_message(
        message=f"Confirm {prepared.pending_action_id}",
        role="Support Operations",
    )

    assert confirmed.success is True
    assert confirmed.structured_data["status"] == "created"


def test_document_search_excludes_deprecated_sources() -> None:
    agent = ParcelPilotAgent()

    response = agent.handle_message(
        message="What are the standard support response targets?",
        role="Support Operations",
    )

    assert response.success is True
    assert "02_Support_Policy_v2_DEPRECATED.pdf" not in response.sources