from app.services.data_service import ParcelPilotDataService


def test_required_sheets_load() -> None:
    service = ParcelPilotDataService()

    assert not service.accounts.empty
    assert not service.orders.empty
    assert not service.tickets.empty


def test_order_lookup() -> None:
    service = ParcelPilotDataService()

    order = service.get_order("ORD-1001")

    assert order is not None
    assert order["account_id"] == "ACCT-001"


def test_customer_cannot_access_other_account_order() -> None:
    service = ParcelPilotDataService()

    order = service.get_order(
        "ORD-1001",
        permitted_account_id="ACCT-002",
    )

    assert order is None


def test_dataset_counts() -> None:
    service = ParcelPilotDataService()
    metrics = service.overview_metrics()

    assert metrics["active_accounts"] == 4
    assert metrics["orders"] == 6
    assert metrics["open_tickets"] == 5
