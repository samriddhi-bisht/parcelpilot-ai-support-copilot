from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentRecord:
    document_id: str
    title: str
    filename: str
    path: Path
    document_type: str
    status: str
    authority_rank: int
    account_id: str | None
    text: str

    @property
    def is_current(self) -> bool:
        return self.status.lower() == "current"

    @property
    def is_deprecated(self) -> bool:
        return self.status.lower() == "deprecated"

    @property
    def authority_label(self) -> str:
        labels = {
            100: "Customer agreement",
            80: "Current policy or SOP",
            70: "Current product documentation",
            20: "Deprecated reference",
        }

        return labels.get(self.authority_rank, "Supporting context")