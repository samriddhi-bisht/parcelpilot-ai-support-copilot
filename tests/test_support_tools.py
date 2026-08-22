from app.tools.support_tools import ParcelPilotSupportTools


def test_northstar_cancellation_uses_contract_override() -> None:
    tools = ParcelPilotSupportTools()

    result = tools.evaluate_cancellation(
        "ORD-1001",
        permitted_account_id="ACCT-001",
    )

    assert result.success is True
    assert result.data["eligible"] is True
    assert result.data["fee_inr"] == 0
    assert result.data["contract_override"] is True


def test_lumenworks_cancellation_has_standard_fee() -> None:
    tools = ParcelPilotSupportTools()

    result = tools.evaluate_cancellation(
        "ORD-2001",
        permitted_account_id="ACCT-002",
    )

    assert result.success is True
    assert result.data["eligible"] is True
    assert result.data["fee_inr"] == 250
    assert result.data["elapsed_minutes"] == 75


def test_beacon_cancellation_within_30_minutes_is_free() -> None:
    tools = ParcelPilotSupportTools()

    result = tools.evaluate_cancellation(
        "ORD-3001",
        permitted_account_id="ACCT-003",
    )

    assert result.success is True
    assert result.data["fee_inr"] == 0
    assert result.data["elapsed_minutes"] == 15


def test_picked_up_order_uses_return_to_origin() -> None:
    tools = ParcelPilotSupportTools()

    result = tools.evaluate_cancellation(
        "ORD-1002",
        permitted_account_id="ACCT-001",
    )

    assert result.success is True
    assert result.data["eligible"] is False
    assert result.data["required_workflow"] == "return_to_origin"


def test_lumenworks_credit_uses_contract_threshold() -> None:
    tools = ParcelPilotSupportTools()

    result = tools.evaluate_service_credit(
        "ORD-2002",
        permitted_account_id="ACCT-002",
    )

    assert result.success is True
    assert result.data["eligible"] is True
    assert result.data["threshold_hours"] == 4.0
    assert result.data["credit_amount_inr"] == 300.0
    assert result.data["contract_override"] is True


def test_ticket_501_is_p1_and_requires_escalation() -> None:
    tools = ParcelPilotSupportTools()

    result = tools.assess_ticket(
        "TKT-501",
        permitted_account_id="ACCT-001",
    )

    assert result.success is True
    assert result.data["severity"] == "P1"
    assert result.data["requires_escalation"] is True


def test_ticket_505_is_p1_security_risk() -> None:
    tools = ParcelPilotSupportTools()

    result = tools.assess_ticket(
        "TKT-505",
        permitted_account_id="ACCT-004",
    )

    assert result.success is True
    assert result.data["severity"] == "P1"
    assert result.data["sla_breached"] is True


def test_cross_account_order_is_blocked() -> None:
    tools = ParcelPilotSupportTools()

    result = tools.evaluate_cancellation(
        "ORD-1001",
        permitted_account_id="ACCT-002",
    )

    assert result.success is False