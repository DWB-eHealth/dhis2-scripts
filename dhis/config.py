import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required env variable: {key}")
    return value

DHIS2_BASE_URL = _require("DHIS2_BASE_URL")
DHIS2_USERNAME = _require("DHIS2_USERNAME")
DHIS2_PASSWORD = _require("DHIS2_PASSWORD")
REPORTS_DIRECTORY = Path(os.getenv("REPORTS_DIRECTORY", "./reports"))
REPORTS_DIRECTORY.mkdir(exist_ok=True)
CASE_NUMBER_COLUMN_ID = _require("CASE_NUMBER_COLUMN_ID")