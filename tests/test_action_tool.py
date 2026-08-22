from pathlib import Path

from app.tools.action_tool import EscalationActionTool


def test_escalation_requires_confirmation(tmp_path: Path) -> None:
    tool = EscalationActionTool(actions_dir=tmp_path)

    prepared = tool.prepare_escalation(
        ticket_id="TKT-501",
        reason="P1 production outage",
        requested_by="Support Operations",
    )

    assert prepared.success is True
    assert prepared.requires_confirmation is True
    assert prepared.pending_action_id is not None

    confirmed = tool.confirm_escalation(
        action_id=prepared.pending_action_id,
        confirmed=True,
    )

    assert confirmed.success is True
    assert confirmed.data["status"] == "created"


def test_escalation_can_be_cancelled(tmp_path: Path) -> None:
    tool = EscalationActionTool(actions_dir=tmp_path)

    prepared = tool.prepare_escalation(
        ticket_id="TKT-505",
        reason="Possible API key exposure",
        requested_by="Support Operations",
    )

    cancelled = tool.confirm_escalation(
        action_id=prepared.pending_action_id,
        confirmed=False,
    )

    assert cancelled.success is True
    assert cancelled.data["status"] == "cancelled"