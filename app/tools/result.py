from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ToolResult:
    tool_name: str
    success: bool
    summary: str
    data: dict[str, Any] = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    requires_confirmation: bool = False
    pending_action_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)