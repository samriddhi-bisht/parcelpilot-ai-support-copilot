from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader

from app.config import DOCUMENTS_DIR
from app.models.document import DocumentRecord


class DocumentServiceError(Exception):
    """Raised when ParcelPilot source documents cannot be loaded."""


class ParcelPilotDocumentService:
    DOCUMENT_CATALOG = {
        "01_Support_Policy_v3_CURRENT.pdf": {
            "document_id": "DOC-POLICY-V3",
            "title": "Support Policy v3",
            "document_type": "support_policy",
            "status": "current",
            "authority_rank": 80,
            "account_id": None,
        },
        "02_Support_Policy_v2_DEPRECATED.pdf": {
            "document_id": "DOC-POLICY-V2",
            "title": "Support Policy v2",
            "document_type": "support_policy",
            "status": "deprecated",
            "authority_rank": 20,
            "account_id": None,
        },
        "03_Cancellation_and_Service_Credit_SOP_v4.pdf": {
            "document_id": "DOC-SOP-V4",
            "title": "Cancellation and Service Credit SOP v4",
            "document_type": "sop",
            "status": "current",
            "authority_rank": 80,
            "account_id": None,
        },
        "04_Product_Operations_Guide_and_Known_Issues.pdf": {
            "document_id": "DOC-PRODUCT-GUIDE",
            "title": "Product Operations Guide and Known Issues",
            "document_type": "product_documentation",
            "status": "current",
            "authority_rank": 70,
            "account_id": None,
        },
        "05_Northstar_Logistics_Enterprise_Agreement.pdf": {
            "document_id": "DOC-NORTHSTAR-AGREEMENT",
            "title": "Northstar Logistics Enterprise Agreement",
            "document_type": "customer_agreement",
            "status": "current",
            "authority_rank": 100,
            "account_id": "ACCT-001",
        },
        "06_LumenWorks_Service_Agreement.pdf": {
            "document_id": "DOC-LUMENWORKS-AGREEMENT",
            "title": "LumenWorks Service Agreement",
            "document_type": "customer_agreement",
            "status": "current",
            "authority_rank": 100,
            "account_id": "ACCT-002",
        },
    }

    def __init__(self, documents_dir: Path | None = None) -> None:
        self.documents_dir = documents_dir or DOCUMENTS_DIR
        self._documents = self._load_documents()

    def _load_documents(self) -> list[DocumentRecord]:
        if not self.documents_dir.exists():
            raise DocumentServiceError(
                f"Document folder does not exist: {self.documents_dir}"
            )

        documents: list[DocumentRecord] = []

        for filename, metadata in self.DOCUMENT_CATALOG.items():
            path = self.documents_dir / filename

            if not path.exists():
                raise DocumentServiceError(
                    f"Required document is missing: {filename}"
                )

            text = self._extract_pdf_text(path)

            documents.append(
                DocumentRecord(
                    document_id=metadata["document_id"],
                    title=metadata["title"],
                    filename=filename,
                    path=path,
                    document_type=metadata["document_type"],
                    status=metadata["status"],
                    authority_rank=metadata["authority_rank"],
                    account_id=metadata["account_id"],
                    text=text,
                )
            )

        return documents

    @staticmethod
    def _extract_pdf_text(path: Path) -> str:
        try:
            reader = PdfReader(path)
        except Exception as exc:
            raise DocumentServiceError(
                f"Could not read PDF: {path.name}"
            ) from exc

        page_texts: list[str] = []

        for page in reader.pages:
            text = page.extract_text() or ""
            page_texts.append(text.strip())

        combined_text = "\n".join(page_texts)
        combined_text = re.sub(r"\s+", " ", combined_text).strip()

        if not combined_text:
            raise DocumentServiceError(
                f"No readable text was found in: {path.name}"
            )

        return combined_text

    @property
    def documents(self) -> list[DocumentRecord]:
        return list(self._documents)

    def list_documents(
        self,
        include_deprecated: bool = False,
    ) -> list[DocumentRecord]:
        documents = self.documents

        if not include_deprecated:
            documents = [
                document
                for document in documents
                if not document.is_deprecated
            ]

        return sorted(
            documents,
            key=lambda document: document.authority_rank,
            reverse=True,
        )

    def search(
        self,
        query: str,
        account_id: str | None = None,
        include_deprecated: bool = False,
        limit: int = 5,
    ) -> list[dict]:
        normalized_query = query.strip().lower()

        if not normalized_query:
            return []

        query_terms = {
            term
            for term in re.findall(r"[a-zA-Z0-9_-]+", normalized_query)
            if len(term) > 2
        }

        results: list[dict] = []

        for document in self.list_documents(
            include_deprecated=include_deprecated
        ):
            if (
                document.document_type == "customer_agreement"
                and document.account_id != account_id
            ):
                continue

            searchable_text = (
                f"{document.title} {document.text}"
            ).lower()

            matching_terms = [
                term for term in query_terms if term in searchable_text
            ]

            if not matching_terms:
                continue

            score = (
                len(matching_terms) * 10
                + document.authority_rank
            )

            snippets = self._extract_snippets(
                document.text,
                matching_terms,
            )

            results.append(
                {
                    "document_id": document.document_id,
                    "title": document.title,
                    "filename": document.filename,
                    "document_type": document.document_type,
                    "status": document.status,
                    "authority_rank": document.authority_rank,
                    "authority_label": document.authority_label,
                    "account_id": document.account_id,
                    "matching_terms": matching_terms,
                    "score": score,
                    "snippets": snippets,
                }
            )

        return sorted(
            results,
            key=lambda result: result["score"],
            reverse=True,
        )[:limit]

    @staticmethod
    def _extract_snippets(
        text: str,
        matching_terms: list[str],
        radius: int = 180,
    ) -> list[str]:
        lowered_text = text.lower()
        snippets: list[str] = []

        for term in matching_terms[:3]:
            position = lowered_text.find(term)

            if position == -1:
                continue

            start = max(0, position - radius)
            end = min(len(text), position + len(term) + radius)

            snippet = text[start:end].strip()

            if start > 0:
                snippet = f"...{snippet}"

            if end < len(text):
                snippet = f"{snippet}..."

            snippets.append(snippet)

        return snippets