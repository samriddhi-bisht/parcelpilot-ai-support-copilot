from app.services.document_service import ParcelPilotDocumentService


def test_all_documents_load() -> None:
    service = ParcelPilotDocumentService()

    assert len(service.documents) == 6


def test_deprecated_policy_excluded_by_default() -> None:
    service = ParcelPilotDocumentService()

    filenames = [
        document.filename
        for document in service.list_documents()
    ]

    assert "02_Support_Policy_v2_DEPRECATED.pdf" not in filenames


def test_northstar_agreement_has_highest_authority() -> None:
    service = ParcelPilotDocumentService()

    results = service.search(
        query="Northstar cancellation fee",
        account_id="ACCT-001",
    )

    assert results
    assert results[0]["document_type"] == "customer_agreement"
    assert results[0]["account_id"] == "ACCT-001"


def test_customer_cannot_search_another_customer_agreement() -> None:
    service = ParcelPilotDocumentService()

    results = service.search(
        query="Northstar cancellation fee",
        account_id="ACCT-002",
    )

    visible_agreement_accounts = {
        result["account_id"]
        for result in results
        if result["document_type"] == "customer_agreement"
    }

    assert "ACCT-001" not in visible_agreement_accounts
    assert visible_agreement_accounts.issubset({"ACCT-002"})


def test_deprecated_policy_can_be_loaded_for_audit_only() -> None:
    service = ParcelPilotDocumentService()

    documents = service.list_documents(
        include_deprecated=True
    )

    deprecated = [
        document
        for document in documents
        if document.is_deprecated
    ]

    assert len(deprecated) == 1