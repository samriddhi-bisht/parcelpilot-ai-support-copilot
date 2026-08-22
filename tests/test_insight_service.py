from app.services.insight_service import ParcelPilotInsightService


def test_dashboard_summary() -> None:
    service = ParcelPilotInsightService()

    summary = service.dashboard_summary()

    assert summary["open_tickets"] == 5
    assert summary["p1_tickets"] >= 1
    assert summary["sla_breaches"] >= 1
    assert summary["requires_escalation"] >= 1


def test_urgent_queue_contains_ticket_501() -> None:
    service = ParcelPilotInsightService()

    ticket_ids = {
        item["ticket_id"]
        for item in service.urgent_queue()
    }

    assert "TKT-501" in ticket_ids


def test_recurring_issues_are_detected() -> None:
    service = ParcelPilotInsightService()

    results = service.detect_recurring_issues()

    assert isinstance(results, list)
    assert len(results) >= 1


def test_known_issue_matches_are_detected() -> None:
    service = ParcelPilotInsightService()

    results = service.detect_known_issue_matches()

    assert isinstance(results, list)


def test_carrier_issue_summary_returns_list() -> None:
    service = ParcelPilotInsightService()

    results = service.carrier_issue_summary()

    assert isinstance(results, list)