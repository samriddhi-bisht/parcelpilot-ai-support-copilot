from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

import pandas as pd

from app.services.data_service import ParcelPilotDataService
from app.tools.support_tools import ParcelPilotSupportTools


SNAPSHOT_TIME = datetime(2026, 8, 16, 11, 0)


class ParcelPilotInsightService:
    def __init__(
        self,
        data_service: ParcelPilotDataService | None = None,
        support_tools: ParcelPilotSupportTools | None = None,
    ) -> None:
        self.data_service = data_service or ParcelPilotDataService()
        self.support_tools = support_tools or ParcelPilotSupportTools(
            data_service=self.data_service
        )

    def dashboard_summary(self) -> dict[str, int]:
        assessed_tickets = self.assess_all_open_tickets()

        p1_count = sum(
            1
            for item in assessed_tickets
            if item["severity"] == "P1"
        )

        breached_count = sum(
            1
            for item in assessed_tickets
            if item["sla_breached"]
        )

        escalation_count = sum(
            1
            for item in assessed_tickets
            if item["requires_escalation"]
        )

        recurring_issue_count = len(
            self.detect_recurring_issues()
        )

        return {
            "open_tickets": len(assessed_tickets),
            "p1_tickets": p1_count,
            "sla_breaches": breached_count,
            "requires_escalation": escalation_count,
            "recurring_issue_groups": recurring_issue_count,
        }

    def assess_all_open_tickets(self) -> list[dict[str, Any]]:
        tickets = self.data_service.tickets.copy()

        open_tickets = tickets[
            tickets["status"].astype(str).str.lower() == "open"
        ]

        results: list[dict[str, Any]] = []

        for _, ticket in open_tickets.iterrows():
            ticket_id = str(ticket["ticket_id"])

            assessment = self.support_tools.assess_ticket(ticket_id)

            if not assessment.success:
                continue

            account = self.data_service.get_account(
                str(ticket["account_id"])
            )

            results.append(
                {
                    "ticket_id": ticket_id,
                    "account_id": ticket["account_id"],
                    "account_name": (
                        account["account_name"]
                        if account
                        else "Unknown account"
                    ),
                    "subject": ticket.get("subject", ""),
                    "status": ticket.get("status", ""),
                    "severity": assessment.data["severity"],
                    "severity_reason": assessment.data[
                        "severity_reason"
                    ],
                    "age_minutes": assessment.data["age_minutes"],
                    "target_minutes": assessment.data[
                        "target_minutes"
                    ],
                    "target_display": assessment.data[
                        "target_display"
                    ],
                    "sla_breached": assessment.data[
                        "sla_breached"
                    ],
                    "requires_escalation": assessment.data[
                        "requires_escalation"
                    ],
                }
            )

        return sorted(
            results,
            key=lambda item: (
                not item["requires_escalation"],
                item["severity"] != "P1",
                not item["sla_breached"],
                -item["age_minutes"],
            ),
        )

    def urgent_queue(self) -> list[dict[str, Any]]:
        return [
            item
            for item in self.assess_all_open_tickets()
            if item["requires_escalation"]
        ]

    def detect_recurring_issues(self) -> list[dict[str, Any]]:
        tickets = self.data_service.tickets.copy()

        open_tickets = tickets[
            tickets["status"].astype(str).str.lower() == "open"
        ]

        issue_patterns = {
            "Bulk upload failure": [
                "bulk upload",
                "csv upload",
                "large csv",
            ],
            "Pickup delay": [
                "pickup",
                "late pickup",
                "pickup delay",
                "webhook delay",
            ],
            "Shipment creation outage": [
                "shipment creation",
                "creation failing",
                "cannot create shipment",
                "outage",
            ],
            "Credential or API security risk": [
                "api key",
                "credential",
                "security",
                "exposure",
            ],
            "Cancellation request": [
                "cancel",
                "cancellation",
            ],
        }

        matches: dict[str, list[dict[str, Any]]] = {
            issue_name: []
            for issue_name in issue_patterns
        }

        for _, ticket in open_tickets.iterrows():
            combined_text = (
                f"{ticket.get('subject', '')} "
                f"{ticket.get('description', '')}"
            ).lower()

            account = self.data_service.get_account(
                str(ticket["account_id"])
            )

            for issue_name, terms in issue_patterns.items():
                if any(term in combined_text for term in terms):
                    matches[issue_name].append(
                        {
                            "ticket_id": ticket["ticket_id"],
                            "account_id": ticket["account_id"],
                            "account_name": (
                                account["account_name"]
                                if account
                                else "Unknown account"
                            ),
                            "subject": ticket.get("subject", ""),
                        }
                    )

        results: list[dict[str, Any]] = []

        for issue_name, matched_tickets in matches.items():
            if not matched_tickets:
                continue

            affected_accounts = sorted(
                {
                    item["account_name"]
                    for item in matched_tickets
                }
            )

            results.append(
                {
                    "issue": issue_name,
                    "ticket_count": len(matched_tickets),
                    "affected_account_count": len(
                        affected_accounts
                    ),
                    "affected_accounts": affected_accounts,
                    "tickets": matched_tickets,
                    "cross_customer": (
                        len(affected_accounts) > 1
                    ),
                }
            )

        return sorted(
            results,
            key=lambda item: (
                not item["cross_customer"],
                -item["ticket_count"],
            ),
        )

    def detect_known_issue_matches(self) -> list[dict[str, Any]]:
        tickets = self.data_service.tickets.copy()

        open_tickets = tickets[
            tickets["status"].astype(str).str.lower() == "open"
        ]

        known_issues = [
            {
                "known_issue_id": "KI-208",
                "title": "Bulk Upload failures on large CSVs",
                "terms": [
                    "bulk upload",
                    "csv",
                    "upload failure",
                ],
                "status": "Investigating",
                "workaround": (
                    "Split uploads into files below 3,000 rows."
                ),
            },
            {
                "known_issue_id": "KI-211",
                "title": "SwiftShip pickup webhook delay",
                "terms": [
                    "swiftship",
                    "pickup confirmation",
                    "webhook",
                    "pickup delay",
                ],
                "status": "Monitoring",
                "workaround": (
                    "Verify carrier status or wait through the "
                    "known 20-minute delay window."
                ),
            },
        ]

        results: list[dict[str, Any]] = []

        for _, ticket in open_tickets.iterrows():
            combined_text = (
                f"{ticket.get('subject', '')} "
                f"{ticket.get('description', '')}"
            ).lower()

            for known_issue in known_issues:
                matching_terms = [
                    term
                    for term in known_issue["terms"]
                    if term in combined_text
                ]

                if not matching_terms:
                    continue

                account = self.data_service.get_account(
                    str(ticket["account_id"])
                )

                results.append(
                    {
                        "ticket_id": ticket["ticket_id"],
                        "account_name": (
                            account["account_name"]
                            if account
                            else "Unknown account"
                        ),
                        "subject": ticket.get("subject", ""),
                        "known_issue_id": known_issue[
                            "known_issue_id"
                        ],
                        "known_issue_title": known_issue["title"],
                        "known_issue_status": known_issue["status"],
                        "workaround": known_issue["workaround"],
                        "matching_terms": matching_terms,
                    }
                )

        return results

    def carrier_issue_summary(self) -> list[dict[str, Any]]:
        orders = self.data_service.orders.copy()

        if "carrier" not in orders.columns:
            return []

        issue_counts: Counter[str] = Counter()

        for _, order in orders.iterrows():
            carrier = str(order.get("carrier", "Unknown"))

            carrier_fault = order.get("carrier_fault")

            if bool(carrier_fault):
                issue_counts[carrier] += 1

        return [
            {
                "carrier": carrier,
                "carrier_fault_orders": count,
            }
            for carrier, count in issue_counts.most_common()
        ]