from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import ACTIONS_DIR
from app.services.data_service import ParcelPilotDataService
from app.tools.result import ToolResult


class EscalationActionTool:
    def __init__(
        self,
        data_service: ParcelPilotDataService | None = None,
        actions_dir: Path | None = None,
    ) -> None:
        self.data_service = data_service or ParcelPilotDataService()
        self.actions_dir = actions_dir or ACTIONS_DIR
        self.actions_dir.mkdir(parents=True, exist_ok=True)
        self.pending_file = self.actions_dir / "pending_actions.json"
        self.completed_file = self.actions_dir / "completed_actions.json"

    def prepare_escalation(
        self,
        ticket_id: str,
        reason: str,
        requested_by: str,
        permitted_account_id: str | None = None,
    ) -> ToolResult:
        ticket = self.data_service.get_ticket(
            ticket_id=ticket_id,
            permitted_account_id=permitted_account_id,
        )

        if ticket is None:
            return ToolResult(
                tool_name="prepare_escalation",
                success=False,
                summary=(
                    "The escalation could not be prepared because the "
                    "ticket was not found or was not accessible."
                ),
            )

        action_id = f"ESC-{uuid.uuid4().hex[:8].upper()}"

        action = {
            "action_id": action_id,
            "action_type": "ticket_escalation",
            "ticket_id": ticket["ticket_id"],
            "account_id": ticket["account_id"],
            "reason": reason.strip(),
            "requested_by": requested_by.strip(),
            "status": "pending_confirmation",
            "prepared_at": datetime.now().isoformat(timespec="seconds"),
        }

        pending_actions = self._read_actions(self.pending_file)
        pending_actions.append(action)
        self._write_actions(self.pending_file, pending_actions)

        return ToolResult(
            tool_name="prepare_escalation",
            success=True,
            summary=(
                f"Escalation {action_id} is prepared but has not been "
                "executed. Explicit confirmation is required."
            ),
            data=action,
            sources=[
                "ParcelPilot_Assessment_Data.xlsx: tickets",
            ],
            requires_confirmation=True,
            pending_action_id=action_id,
        )

    def confirm_escalation(
        self,
        action_id: str,
        confirmed: bool,
    ) -> ToolResult:
        pending_actions = self._read_actions(self.pending_file)

        matching_action = next(
            (
                action
                for action in pending_actions
                if action["action_id"] == action_id
            ),
            None,
        )

        if matching_action is None:
            return ToolResult(
                tool_name="confirm_escalation",
                success=False,
                summary="The pending action could not be found.",
            )

        remaining_actions = [
            action
            for action in pending_actions
            if action["action_id"] != action_id
        ]

        self._write_actions(self.pending_file, remaining_actions)

        if not confirmed:
            matching_action["status"] = "cancelled"
            matching_action["resolved_at"] = datetime.now().isoformat(
                timespec="seconds"
            )

            completed_actions = self._read_actions(self.completed_file)
            completed_actions.append(matching_action)
            self._write_actions(
                self.completed_file,
                completed_actions,
            )

            return ToolResult(
                tool_name="confirm_escalation",
                success=True,
                summary=(
                    f"Escalation {action_id} was cancelled and no "
                    "state-changing action was executed."
                ),
                data=matching_action,
            )

        matching_action["status"] = "created"
        matching_action["confirmed_at"] = datetime.now().isoformat(
            timespec="seconds"
        )

        completed_actions = self._read_actions(self.completed_file)
        completed_actions.append(matching_action)
        self._write_actions(
            self.completed_file,
            completed_actions,
        )

        return ToolResult(
            tool_name="confirm_escalation",
            success=True,
            summary=(
                f"Escalation {action_id} was confirmed and created."
            ),
            data=matching_action,
        )

    @staticmethod
    def _read_actions(path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []

        try:
            content = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

        return content if isinstance(content, list) else []

    @staticmethod
    def _write_actions(
        path: Path,
        actions: list[dict[str, Any]],
    ) -> None:
        path.write_text(
            json.dumps(actions, indent=2, default=str),
            encoding="utf-8",
        )