from __future__ import annotations

import re
from typing import Any

from app.agent.response import AgentResponse
from app.services.document_service import ParcelPilotDocumentService
from app.tools.action_tool import EscalationActionTool
from app.tools.result import ToolResult
from app.tools.support_tools import ParcelPilotSupportTools


class ParcelPilotAgent:
    ORDER_PATTERN = re.compile(r"\bORD-\d+\b", re.IGNORECASE)
    TICKET_PATTERN = re.compile(r"\bTKT-\d+\b", re.IGNORECASE)
    ACTION_PATTERN = re.compile(r"\bESC-[A-Z0-9]+\b", re.IGNORECASE)

    def __init__(
        self,
        support_tools: ParcelPilotSupportTools | None = None,
        document_service: ParcelPilotDocumentService | None = None,
        action_tool: EscalationActionTool | None = None,
    ) -> None:
        self.support_tools = support_tools or ParcelPilotSupportTools()
        self.document_service = (
            document_service or ParcelPilotDocumentService()
        )
        self.action_tool = action_tool or EscalationActionTool()

    def handle_message(
        self,
        message: str,
        role: str,
        account_id: str | None = None,
    ) -> AgentResponse:
        cleaned_message = message.strip()

        if not cleaned_message:
            return AgentResponse(
                answer="Enter a support or operations question.",
                intent="empty_request",
                success=False,
                confidence="low",
            )

        normalized = cleaned_message.lower()
        order_id = self._extract_first(
            self.ORDER_PATTERN,
            cleaned_message,
        )
        ticket_id = self._extract_first(
            self.TICKET_PATTERN,
            cleaned_message,
        )
        action_id = self._extract_first(
            self.ACTION_PATTERN,
            cleaned_message,
        )

        permitted_account_id = (
            account_id if role.lower() == "customer" else None
        )

        if action_id and self._contains_any(
            normalized,
            ["confirm", "approve", "proceed", "yes"],
        ):
            return self._confirm_action(
                action_id=action_id,
                confirmed=True,
                role=role,
            )

        if action_id and self._contains_any(
            normalized,
            ["cancel action", "reject", "do not proceed", "decline"],
        ):
            return self._confirm_action(
                action_id=action_id,
                confirmed=False,
                role=role,
            )

        if self._contains_any(
            normalized,
            ["escalate", "create escalation", "raise escalation"],
        ):
            return self._prepare_escalation(
                ticket_id=ticket_id,
                message=cleaned_message,
                role=role,
                permitted_account_id=permitted_account_id,
            )

        if order_id and self._contains_any(
            normalized,
            [
                "cancel",
                "cancellation",
                "cancellation fee",
                "without a fee",
            ],
        ):
            result = self.support_tools.evaluate_cancellation(
                order_id=order_id,
                permitted_account_id=permitted_account_id,
            )

            return self._response_from_tool(
                intent="cancellation_decision",
                result=result,
            )

        if order_id and self._contains_any(
            normalized,
            [
                "credit",
                "service credit",
                "pickup late",
                "late pickup",
                "failed pickup",
            ],
        ):
            result = self.support_tools.evaluate_service_credit(
                order_id=order_id,
                permitted_account_id=permitted_account_id,
            )

            return self._response_from_tool(
                intent="service_credit_decision",
                result=result,
            )

        if ticket_id and self._contains_any(
            normalized,
            [
                "severity",
                "priority",
                "sla",
                "breach",
                "assess",
                "triage",
                "urgent",
            ],
        ):
            result = self.support_tools.assess_ticket(
                ticket_id=ticket_id,
                permitted_account_id=permitted_account_id,
            )

            return self._response_from_tool(
                intent="ticket_assessment",
                result=result,
            )

        if order_id:
            result = self.support_tools.lookup_order(
                order_id=order_id,
                permitted_account_id=permitted_account_id,
            )

            return self._response_from_tool(
                intent="order_lookup",
                result=result,
            )

        if ticket_id:
            result = self.support_tools.lookup_ticket(
                ticket_id=ticket_id,
                permitted_account_id=permitted_account_id,
            )

            return self._response_from_tool(
                intent="ticket_lookup",
                result=result,
            )

        return self._search_documents(
            query=cleaned_message,
            account_id=permitted_account_id,
        )

    def _prepare_escalation(
        self,
        ticket_id: str | None,
        message: str,
        role: str,
        permitted_account_id: str | None,
    ) -> AgentResponse:
        if role.lower() == "customer":
            return AgentResponse(
                answer=(
                    "Customers cannot directly create internal escalations. "
                    "I can identify whether the issue should be escalated "
                    "and route it to the support team."
                ),
                intent="escalation_not_authorised",
                success=False,
                warnings=[
                    "State-changing internal actions require an authorised "
                    "support or operations role."
                ],
                confidence="high",
            )

        if ticket_id is None:
            return AgentResponse(
                answer=(
                    "Provide the ticket ID to prepare an escalation, "
                    "for example: escalate TKT-501."
                ),
                intent="prepare_escalation",
                success=False,
                confidence="low",
            )

        assessment = self.support_tools.assess_ticket(
            ticket_id=ticket_id,
            permitted_account_id=permitted_account_id,
        )

        if not assessment.success:
            return self._response_from_tool(
                intent="prepare_escalation",
                result=assessment,
            )

        reason = self._build_escalation_reason(
            message=message,
            assessment=assessment,
        )

        prepared = self.action_tool.prepare_escalation(
            ticket_id=ticket_id,
            reason=reason,
            requested_by=role,
            permitted_account_id=permitted_account_id,
        )

        traces = [
            self._tool_trace(assessment),
            self._tool_trace(prepared),
        ]

        sources = self._unique(
            assessment.sources + prepared.sources
        )

        warnings = self._unique(
            assessment.warnings + prepared.warnings
        )

        return AgentResponse(
            answer=(
                f"{assessment.summary}\n\n"
                f"{prepared.summary}\n\n"
                f"Confirm action {prepared.pending_action_id} to create "
                "the escalation, or cancel it."
            ),
            intent="prepare_escalation",
            success=prepared.success,
            tool_traces=traces,
            sources=sources,
            warnings=warnings,
            confidence="high",
            requires_confirmation=True,
            pending_action_id=prepared.pending_action_id,
            structured_data={
                "assessment": assessment.data,
                "pending_action": prepared.data,
            },
        )

    def _confirm_action(
        self,
        action_id: str,
        confirmed: bool,
        role: str,
    ) -> AgentResponse:
        if role.lower() == "customer":
            return AgentResponse(
                answer=(
                    "This action can only be confirmed by an authorised "
                    "support or operations user."
                ),
                intent="confirm_escalation",
                success=False,
                confidence="high",
            )

        result = self.action_tool.confirm_escalation(
            action_id=action_id.upper(),
            confirmed=confirmed,
        )

        return self._response_from_tool(
            intent="confirm_escalation",
            result=result,
        )

    def _search_documents(
        self,
        query: str,
        account_id: str | None,
    ) -> AgentResponse:
        results = self.document_service.search(
            query=query,
            account_id=account_id,
            include_deprecated=False,
            limit=4,
        )

        if not results:
            return AgentResponse(
                answer=(
                    "I could not find enough authoritative information in "
                    "the supplied ParcelPilot sources to answer confidently. "
                    "The request should be reviewed by the support team."
                ),
                intent="document_search",
                success=False,
                warnings=[
                    "No sufficiently relevant current source was found."
                ],
                confidence="low",
            )

        top_result = results[0]

        evidence_lines: list[str] = []

        for result in results[:3]:
            snippet = (
                result["snippets"][0]
                if result["snippets"]
                else "Relevant source matched."
            )

            evidence_lines.append(
                f"{result['title']}: {snippet}"
            )

        answer = (
            "I found the following relevant guidance:\n\n"
            + "\n\n".join(evidence_lines)
        )

        sources = [
            result["filename"]
            for result in results
        ]

        tool_trace = {
            "tool_name": "document_search",
            "success": True,
            "summary": (
                f"Found {len(results)} current, accessible source matches."
            ),
            "data": {
                "results": results,
                "highest_authority_source": top_result["title"],
            },
        }

        confidence = (
            "high"
            if top_result["authority_rank"] >= 80
            else "medium"
        )

        return AgentResponse(
            answer=answer,
            intent="document_search",
            success=True,
            tool_traces=[tool_trace],
            sources=sources,
            confidence=confidence,
            structured_data={
                "search_results": results,
            },
        )

    @staticmethod
    def _response_from_tool(
        intent: str,
        result: ToolResult,
    ) -> AgentResponse:
        confidence = "high" if result.success else "low"

        return AgentResponse(
            answer=result.summary,
            intent=intent,
            success=result.success,
            tool_traces=[
                ParcelPilotAgent._tool_trace(result)
            ],
            sources=result.sources,
            warnings=result.warnings,
            confidence=confidence,
            requires_confirmation=result.requires_confirmation,
            pending_action_id=result.pending_action_id,
            structured_data=result.data,
        )

    @staticmethod
    def _tool_trace(result: ToolResult) -> dict[str, Any]:
        return {
            "tool_name": result.tool_name,
            "success": result.success,
            "summary": result.summary,
            "data": result.data,
        }

    @staticmethod
    def _extract_first(
        pattern: re.Pattern[str],
        message: str,
    ) -> str | None:
        match = pattern.search(message)

        if not match:
            return None

        return match.group(0).upper()

    @staticmethod
    def _contains_any(
        message: str,
        phrases: list[str],
    ) -> bool:
        return any(phrase in message for phrase in phrases)

    @staticmethod
    def _unique(values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))

    @staticmethod
    def _build_escalation_reason(
        message: str,
        assessment: ToolResult,
    ) -> str:
        severity = assessment.data.get("severity", "Unclassified")
        breached = assessment.data.get("sla_breached", False)

        parts = [
            f"Requested through support workspace. Severity: {severity}.",
        ]

        if breached:
            parts.append("Applicable first-response target is breached.")

        parts.append(f"User request: {message}")

        return " ".join(parts)