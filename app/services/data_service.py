from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app.config import DATA_DIR


class DataServiceError(Exception):
    """Raised when the ParcelPilot structured dataset cannot be loaded."""


class ParcelPilotDataService:
    REQUIRED_SHEETS = {"README", "accounts", "orders", "tickets"}

    def __init__(self, workbook_path: Path | None = None) -> None:
        self.workbook_path = workbook_path or self._find_workbook()
        self._sheets = self._load_workbook()

    def _find_workbook(self) -> Path:
        workbooks = sorted(DATA_DIR.glob("*.xlsx"))

        if not workbooks:
            raise DataServiceError(
                "No Excel workbook was found inside the data folder."
            )

        return workbooks[0]

    def _load_workbook(self) -> dict[str, pd.DataFrame]:
        try:
            excel_file = pd.ExcelFile(self.workbook_path)
        except Exception as exc:
            raise DataServiceError(
                f"Could not open workbook: {self.workbook_path.name}"
            ) from exc

        missing_sheets = self.REQUIRED_SHEETS.difference(excel_file.sheet_names)

        if missing_sheets:
            missing = ", ".join(sorted(missing_sheets))
            raise DataServiceError(
                f"Workbook is missing required sheets: {missing}"
            )

        sheets: dict[str, pd.DataFrame] = {}

        for sheet_name in self.REQUIRED_SHEETS:
            dataframe = pd.read_excel(
                self.workbook_path,
                sheet_name=sheet_name,
            )
            dataframe.columns = [
                str(column).strip() for column in dataframe.columns
            ]
            sheets[sheet_name] = dataframe

        return sheets

    @property
    def accounts(self) -> pd.DataFrame:
        return self._sheets["accounts"].copy()

    @property
    def orders(self) -> pd.DataFrame:
        return self._sheets["orders"].copy()

    @property
    def tickets(self) -> pd.DataFrame:
        return self._sheets["tickets"].copy()

    def dataset_metadata(self) -> dict[str, str]:
        readme = self._sheets["README"]

        if readme.shape[1] < 2:
            return {}

        key_column = readme.columns[0]
        value_column = readme.columns[1]

        metadata: dict[str, str] = {}

        for _, row in readme.iterrows():
            key = str(row[key_column]).strip()
            value = str(row[value_column]).strip()

            if key and key.lower() != "nan":
                metadata[key] = value

        return metadata

    def list_accounts(self) -> list[dict[str, Any]]:
        columns = [
            "account_id",
            "account_name",
            "plan",
            "status",
            "csm",
            "premium_support",
        ]

        available_columns = [
            column for column in columns if column in self.accounts.columns
        ]

        return (
            self.accounts[available_columns]
            .fillna("")
            .to_dict(orient="records")
        )

    def get_account(self, account_id: str) -> dict[str, Any] | None:
        match = self.accounts[
            self.accounts["account_id"].astype(str) == str(account_id)
        ]

        if match.empty:
            return None

        return match.iloc[0].fillna("").to_dict()

    def get_order(
        self,
        order_id: str,
        permitted_account_id: str | None = None,
    ) -> dict[str, Any] | None:
        orders = self.orders[
            self.orders["order_id"].astype(str).str.upper()
            == str(order_id).strip().upper()
        ]

        if permitted_account_id:
            orders = orders[
                orders["account_id"].astype(str)
                == str(permitted_account_id)
            ]

        if orders.empty:
            return None

        return orders.iloc[0].fillna("").to_dict()

    def get_ticket(
        self,
        ticket_id: str,
        permitted_account_id: str | None = None,
    ) -> dict[str, Any] | None:
        tickets = self.tickets[
            self.tickets["ticket_id"].astype(str).str.upper()
            == str(ticket_id).strip().upper()
        ]

        if permitted_account_id:
            tickets = tickets[
                tickets["account_id"].astype(str)
                == str(permitted_account_id)
            ]

        if tickets.empty:
            return None

        return tickets.iloc[0].fillna("").to_dict()

    def get_account_orders(self, account_id: str) -> pd.DataFrame:
        return self.orders[
            self.orders["account_id"].astype(str) == str(account_id)
        ].copy()

    def get_account_tickets(self, account_id: str) -> pd.DataFrame:
        return self.tickets[
            self.tickets["account_id"].astype(str) == str(account_id)
        ].copy()

    def overview_metrics(self) -> dict[str, int]:
        open_tickets = self.tickets[
            self.tickets["status"].astype(str).str.lower() == "open"
        ]

        active_accounts = self.accounts[
            self.accounts["status"].astype(str).str.lower() == "active"
        ]

        return {
            "active_accounts": len(active_accounts),
            "orders": len(self.orders),
            "open_tickets": len(open_tickets),
            "carriers": self.orders["carrier"].nunique(),
        }
