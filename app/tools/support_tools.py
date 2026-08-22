from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from app.services.data_service import ParcelPilotDataService
from app.tools.result import ToolResult


SNAPSHOT_TIME = datetime(2026, 8, 16, 11, 0)


class ParcelPilotSupportTools:
    def __init__(
        self,
        data_service: ParcelPilotDataService | None = None,
    ) -> None:
        self.data_service = data_service or ParcelPilotDataService()

    @staticmethod
    def _to_datetime(value: Any) -> datetime | None:
        if value is None or pd.isna(value) or str(value).strip() == "":
            return None

        parsed = pd.to_datetime(value, errors="coerce")

        if pd.isna(parsed):
            return None

        return parsed.to_pydatetime()

    def lookup_order(
        self,
        order_id: str,
        permitted_account_id: str | None = None,
    ) -> ToolResult:
        order = self.data_service.get_order(
            order_id=order_id,
            permitted_account_id=permitted_account_id,
        )

        if order is None:
            return ToolResult(
                tool_name="structured_order_lookup",
                success=False,
                summary=(
                    "No accessible order was found with that identifier."
                ),
                warnings=[
                    "The order may not exist or may belong to another account."
                ],
            )

        account = self.data_service.get_account(order["account_id"])

        return ToolResult(
            tool_name="structured_order_lookup",
            success=True,
            summary=f"Order {order['order_id']} was found.",
            data={
                "order": order,
                "account": account,
            },
            sources=[
                "ParcelPilot_Assessment_Data.xlsx: orders",
                "ParcelPilot_Assessment_Data.xlsx: accounts",
            ],
        )

    def lookup_ticket(
        self,
        ticket_id: str,
        permitted_account_id: str | None = None,
    ) -> ToolResult:
        ticket = self.data_service.get_ticket(
            ticket_id=ticket_id,
            permitted_account_id=permitted_account_id,
        )

        if ticket is None:
            return ToolResult(
                tool_name="structured_ticket_lookup",
                success=False,
                summary=(
                    "No accessible ticket was found with that identifier."
                ),
                warnings=[
                    "The ticket may not exist or may belong to another account."
                ],
            )

        account = self.data_service.get_account(ticket["account_id"])

        safe_ticket = {
            key: value
            for key, value in ticket.items()
            if key != "historical_resolution"
        }

        return ToolResult(
            tool_name="structured_ticket_lookup",
            success=True,
            summary=f"Ticket {ticket['ticket_id']} was found.",
            data={
                "ticket": safe_ticket,
                "account": account,
            },
            sources=[
                "ParcelPilot_Assessment_Data.xlsx: tickets",
                "ParcelPilot_Assessment_Data.xlsx: accounts",
            ],
            warnings=[
                "Historical resolutions are excluded from policy decisions."
            ],
        )

    def evaluate_cancellation(
        self,
        order_id: str,
        permitted_account_id: str | None = None,
    ) -> ToolResult:
        order = self.data_service.get_order(
            order_id=order_id,
            permitted_account_id=permitted_account_id,
        )

        if order is None:
            return ToolResult(
                tool_name="cancellation_rule_engine",
                success=False,
                summary=(
                    "The cancellation decision could not be calculated "
                    "because the order was not found or was not accessible."
                ),
            )

        account = self.data_service.get_account(order["account_id"])

        if account is None:
            return ToolResult(
                tool_name="cancellation_rule_engine",
                success=False,
                summary="The account linked to the order was not found.",
            )

        status = str(order["status"]).upper()
        order_id_value = str(order["order_id"])
        account_id = str(order["account_id"])

        sources = [
            "03_Cancellation_and_Service_Credit_SOP_v4.pdf",
            "ParcelPilot_Assessment_Data.xlsx: orders",
        ]

        if status == "DRAFT":
            return ToolResult(
                tool_name="cancellation_rule_engine",
                success=True,
                summary=(
                    f"{order_id_value} may be cancelled without a fee."
                ),
                data={
                    "order_id": order_id_value,
                    "eligible": True,
                    "fee_inr": 0,
                    "reason": "DRAFT shipments may be cancelled without a fee.",
                },
                sources=sources,
            )

        if status == "PICKED_UP":
            return ToolResult(
                tool_name="cancellation_rule_engine",
                success=True,
                summary=(
                    f"{order_id_value} cannot be cancelled because pickup "
                    "has already occurred. Use the return-to-origin workflow."
                ),
                data={
                    "order_id": order_id_value,
                    "eligible": False,
                    "fee_inr": None,
                    "required_workflow": "return_to_origin",
                    "reason": "The shipment is already PICKED_UP.",
                },
                sources=sources,
            )

        if status == "DELIVERED":
            return ToolResult(
                tool_name="cancellation_rule_engine",
                success=True,
                summary=(
                    f"{order_id_value} cannot be cancelled because it has "
                    "already been delivered."
                ),
                data={
                    "order_id": order_id_value,
                    "eligible": False,
                    "fee_inr": None,
                    "reason": "Delivered shipments cannot be cancelled.",
                },
                sources=sources,
            )

        if status != "BOOKED":
            return ToolResult(
                tool_name="cancellation_rule_engine",
                success=False,
                summary=(
                    f"Cancellation rules are not defined for status {status}."
                ),
                warnings=["Human review is required."],
            )

        if account_id == "ACCT-001":
            sources.insert(
                0,
                "05_Northstar_Logistics_Enterprise_Agreement.pdf",
            )

            return ToolResult(
                tool_name="cancellation_rule_engine",
                success=True,
                summary=(
                    f"{order_id_value} may be cancelled without a fee "
                    "because Northstar's signed agreement overrides the "
                    "default cancellation rule."
                ),
                data={
                    "order_id": order_id_value,
                    "eligible": True,
                    "fee_inr": 0,
                    "contract_override": True,
                    "reason": (
                        "Northstar may cancel any BOOKED shipment before "
                        "pickup without a cancellation fee."
                    ),
                },
                sources=sources,
            )

        booked_at = self._to_datetime(order.get("booked_at"))
        requested_at = self._to_datetime(
            order.get("cancellation_requested_at")
        )

        if booked_at is None or requested_at is None:
            return ToolResult(
                tool_name="cancellation_rule_engine",
                success=False,
                summary=(
                    "The cancellation fee cannot be determined because "
                    "booking or request timing is missing."
                ),
                sources=sources,
                warnings=["Request human verification before taking action."],
            )

        elapsed_minutes = int(
            (requested_at - booked_at).total_seconds() / 60
        )

        fee = 0 if elapsed_minutes <= 30 else 250

        return ToolResult(
            tool_name="cancellation_rule_engine",
            success=True,
            summary=(
                f"{order_id_value} may be cancelled with "
                f"{'no fee' if fee == 0 else 'an INR 250 fee'}."
            ),
            data={
                "order_id": order_id_value,
                "eligible": True,
                "fee_inr": fee,
                "elapsed_minutes": elapsed_minutes,
                "contract_override": False,
                "reason": (
                    "BOOKED shipments are free to cancel within 30 minutes; "
                    "after 30 minutes the standard fee is INR 250."
                ),
            },
            sources=sources,
        )

    def evaluate_service_credit(
        self,
        order_id: str,
        permitted_account_id: str | None = None,
    ) -> ToolResult:
        order = self.data_service.get_order(
            order_id=order_id,
            permitted_account_id=permitted_account_id,
        )

        if order is None:
            return ToolResult(
                tool_name="service_credit_rule_engine",
                success=False,
                summary=(
                    "The service-credit decision could not be calculated "
                    "because the order was not found or was not accessible."
                ),
            )

        pickup_window_end = self._to_datetime(
            order.get("pickup_window_end")
        )

        if pickup_window_end is None:
            return ToolResult(
                tool_name="service_credit_rule_engine",
                success=False,
                summary="The pickup-window end time is unavailable.",
                warnings=["Human verification is required."],
            )

        actual_pickup = self._to_datetime(order.get("pickup_actual_at"))
        comparison_time = actual_pickup or SNAPSHOT_TIME

        delay_hours = (
            comparison_time - pickup_window_end
        ).total_seconds() / 3600

        carrier_fault = bool(order.get("carrier_fault"))
        customer_fault = bool(order.get("customer_fault"))
        account_id = str(order["account_id"])
        shipment_fee = float(order["shipment_fee_inr"])

        threshold_hours = 2.0
        credit_amount = min(500.0, shipment_fee * 0.10)

        sources = [
            "03_Cancellation_and_Service_Credit_SOP_v4.pdf",
            "ParcelPilot_Assessment_Data.xlsx: orders",
        ]

        contract_override = False

        if account_id == "ACCT-002":
            threshold_hours = 4.0
            credit_amount = 300.0
            contract_override = True
            sources.insert(
                0,
                "06_LumenWorks_Service_Agreement.pdf",
            )

        facts_known = carrier_fault is not None and customer_fault is not None

        if not facts_known:
            return ToolResult(
                tool_name="service_credit_rule_engine",
                success=False,
                summary=(
                    "Eligibility cannot be confirmed because fault data "
                    "is incomplete."
                ),
                sources=sources,
                warnings=["Do not promise a credit before verification."],
            )

        eligible = (
            delay_hours > threshold_hours
            and carrier_fault
            and not customer_fault
        )

        if eligible:
            summary = (
                f"{order['order_id']} is eligible for an "
                f"INR {credit_amount:.0f} service credit."
            )
        else:
            summary = (
                f"{order['order_id']} is not currently eligible for a "
                "service credit under the applicable rules."
            )

        return ToolResult(
            tool_name="service_credit_rule_engine",
            success=True,
            summary=summary,
            data={
                "order_id": order["order_id"],
                "eligible": eligible,
                "delay_hours": round(delay_hours, 2),
                "threshold_hours": threshold_hours,
                "carrier_fault": carrier_fault,
                "customer_fault": customer_fault,
                "credit_amount_inr": (
                    credit_amount if eligible else 0
                ),
                "contract_override": contract_override,
                "comparison_time": comparison_time.isoformat(),
            },
            sources=sources,
        )

    def assess_ticket(
        self,
        ticket_id: str,
        permitted_account_id: str | None = None,
    ) -> ToolResult:
        ticket = self.data_service.get_ticket(
            ticket_id=ticket_id,
            permitted_account_id=permitted_account_id,
        )

        if ticket is None:
            return ToolResult(
                tool_name="ticket_triage_rule_engine",
                success=False,
                summary=(
                    "The ticket could not be assessed because it was not "
                    "found or was not accessible."
                ),
            )

        account = self.data_service.get_account(ticket["account_id"])

        if account is None:
            return ToolResult(
                tool_name="ticket_triage_rule_engine",
                success=False,
                summary="The ticket account could not be found.",
            )

        combined_text = (
            f"{ticket.get('subject', '')} "
            f"{ticket.get('description', '')}"
        ).lower()

        p1_terms = [
            "all shipment creation is failing",
            "complete outage",
            "security incident",
            "credential exposure",
            "api key exposure",
            "production api key",
        ]

        p2_terms = [
            "major feature",
            "bulk upload fails",
            "materially degraded",
            "unavailable",
        ]

        if any(term in combined_text for term in p1_terms):
            severity = "P1"
            severity_reason = (
                "The issue indicates a complete production outage or "
                "possible credential exposure."
            )
        elif any(term in combined_text for term in p2_terms):
            severity = "P2"
            severity_reason = (
                "A major feature is degraded, but a workaround or core "
                "operation remains available."
            )
        else:
            severity = "P3"
            severity_reason = (
                "The request is a limited-impact issue or how-to question."
            )

        target_minutes = self._response_target_minutes(
            account_id=str(account["account_id"]),
            plan=str(account["plan"]),
            severity=severity,
        )

        created_at = self._to_datetime(ticket.get("created_at"))

        if created_at is None:
            return ToolResult(
                tool_name="ticket_triage_rule_engine",
                success=False,
                summary="Ticket creation time is missing.",
                warnings=["SLA status requires human verification."],
            )

        age_minutes = int(
            (SNAPSHOT_TIME - created_at).total_seconds() / 60
        )

        breached = age_minutes > target_minutes

        sources = [
            "01_Support_Policy_v3_CURRENT.pdf",
            "ParcelPilot_Assessment_Data.xlsx: tickets",
            "ParcelPilot_Assessment_Data.xlsx: accounts",
        ]

        if str(account["account_id"]) == "ACCT-001":
            sources.insert(
                0,
                "05_Northstar_Logistics_Enterprise_Agreement.pdf",
            )

        if str(account["account_id"]) == "ACCT-002":
            sources.insert(
                0,
                "06_LumenWorks_Service_Agreement.pdf",
            )

        requires_escalation = severity == "P1" or breached

        return ToolResult(
            tool_name="ticket_triage_rule_engine",
            success=True,
            summary=(
                f"{ticket['ticket_id']} is assessed as {severity}. "
                f"The first-response target is "
                f"{self._format_minutes(target_minutes)}. "
                f"The target is {'breached' if breached else 'not breached'}."
            ),
            data={
                "ticket_id": ticket["ticket_id"],
                "severity": severity,
                "severity_reason": severity_reason,
                "age_minutes": age_minutes,
                "target_minutes": target_minutes,
                "target_display": self._format_minutes(target_minutes),
                "sla_breached": breached,
                "requires_escalation": requires_escalation,
            },
            sources=sources,
            warnings=(
                ["Immediate escalation is recommended."]
                if requires_escalation
                else []
            ),
        )

    @staticmethod
    def _response_target_minutes(
        account_id: str,
        plan: str,
        severity: str,
    ) -> int:
        if account_id == "ACCT-001":
            return {
                "P1": 15,
                "P2": 60,
                "P3": 480,
            }[severity]

        if account_id == "ACCT-002":
            return {
                "P1": 120,
                "P2": 240,
                "P3": 960,
            }[severity]

        standard_targets = {
            "Enterprise": {
                "P1": 30,
                "P2": 120,
                "P3": 480,
            },
            "Growth": {
                "P1": 120,
                "P2": 240,
                "P3": 960,
            },
            "Standard": {
                "P1": 240,
                "P2": 480,
                "P3": 960,
            },
        }

        plan_targets = standard_targets.get(
            plan,
            standard_targets["Standard"],
        )

        return plan_targets[severity]

    @staticmethod
    def _format_minutes(minutes: int) -> str:
        if minutes < 60:
            return f"{minutes} minutes"

        if minutes % 60 == 0:
            hours = minutes // 60
            return f"{hours} hour" if hours == 1 else f"{hours} hours"

        return f"{minutes} minutes"