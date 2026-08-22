from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class AgentResponse:
    answer: str
    intent: str
    success: bool = True
    tool_traces: list[dict[str, Any]] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    confidence: str = "medium"
    requires_confirmation: bool = False
    pending_action_id: str | None = None
    structured_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)