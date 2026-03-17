import re
from datetime import datetime

def extract_uids_from_expression(expression: str):
    if not expression:
        return []
    return re.findall(r"[A-Za-z0-9]{11}", expression)

# Parsing date from tei
def parse_date(date_str: str):
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d")
    except Exception:
        return None

# Comparing dates for tei DQA analysis
def compare_dates(admission, discharge):
    if not admission or not discharge:
        return "missing data"

    if admission == discharge:
        return "Same admission and discharge date"
    if admission > discharge:
        return "Admission date registered after discharge date"
    return "Discharge date different from admission date"
