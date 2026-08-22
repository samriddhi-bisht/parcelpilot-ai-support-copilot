from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
ACTIONS_DIR = DATA_DIR / "actions"

APP_NAME = "ParcelPilot Control Desk"
APP_TAGLINE = "Reliable support intelligence for logistics operations"

SNAPSHOT_TIME = "2026-08-16 11:00 Asia/Kolkata"

CUSTOMER_ROLE = "Customer"
INTERNAL_ROLE = "Support Operations"
