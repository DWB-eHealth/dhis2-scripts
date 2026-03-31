import random
import string
import json
import re
from datetime import datetime
from collections import Counter
from pathlib import Path

REPORTS_DIRECTORY = Path("reports")

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

# dashboard uid generator
def dhis2_uid():
    letters = string.ascii_letters
    chars = string.ascii_letters + string.digits
    return random.choice(letters) + ''.join(random.choice(chars) for _ in range(10))

# detect common title parts across all items and offer replacement for selected items
def detect_and_replace_common_title_parts(all_items, selected_items):
    # detect repeated words across ALL items
    all_titles = [item["name"] for item in all_items]
    word_lists = [t.replace("_", " ").replace("-", " ").split() for t in all_titles]

    word_counter = Counter()
    for words in word_lists:
        word_counter.update(set(words))

    common_words = [w for w, c in word_counter.items() if c >= 2 and len(w) > 2]

    if not common_words:
        print("\nNo common title parts detected.")
        return selected_items

    print("\nCommon title parts:")
    for idx, w in enumerate(common_words, start=1):
        print(f"{idx}. {w}")

    choice = input(
        "Choose word/term number(s) to replace (comma-separated), or press Enter to skip: "
    ).strip()

    if not choice:
        return selected_items

    try:
        indices = [int(x.strip()) for x in choice.split(",") if x.strip()]
        chosen_terms = [common_words[i - 1] for i in indices]
    except Exception:
        print("Invalid choice, skipping replacement.")
        return selected_items

    # ask for replacement for each chosen term
    replacements = {}
    for term in chosen_terms:
        replacement = input(f"Replace '{term}' with: ").strip()
        if replacement:
            replacements[term] = replacement

    if not replacements:
        print("No valid replacements provided, skipping.")
        return selected_items

    changed_items = []

    # apply replacements only to selected items
    for item in selected_items:
        original = item["name"]
        new_name = original

        for old, new in replacements.items():
            new_name = new_name.replace(old, new)

        if new_name != original:
            item["name"] = new_name
            changed_items.append(item)

    # only show logs if something changed
    if changed_items:
        print("\nApplied replacements:")
        for old, new in replacements.items():
            print(f"  {old} → {new}")
    else:
        print("\nNo selected items contained the chosen terms. No changes applied.")

    return selected_items

# dashboard JSON export
def export_dashboard_json(metadata):
    # ensure reports directory exists
    REPORTS_DIRECTORY.mkdir(exist_ok=True)

    # find next available filename
    base = REPORTS_DIRECTORY / "dashboard_export"
    counter = 0

    while True:
        suffix = f"_{counter}" if counter > 0 else ""
        path = Path(f"{base}{suffix}.json")
        if not path.exists():
            break
        counter += 1

    # write JSON file
    with path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nDashboard JSON exported to: {path}")
    return path


# Dashboard related functions
# uid generator
def dhis2_uid():
    # generate a DHIS2‑compatible UID
    letters = string.ascii_letters
    chars = string.ascii_letters + string.digits
    return random.choice(letters) + ''.join(random.choice(chars) for _ in range(10))

# detect common title parts across all items and offer replacement for selected items
def detect_and_replace_common_title_parts(all_items, selected_items):
    # detect repeated words across ALL items
    all_titles = [item["name"] for item in all_items]
    word_lists = [t.replace("_", " ").replace("-", " ").split() for t in all_titles]

    word_counter = Counter()
    for words in word_lists:
        word_counter.update(set(words))

    common_words = [w for w, c in word_counter.items() if c >= 2 and len(w) > 2]

    if not common_words:
        print("\nNo common title parts detected.")
        return selected_items

    print("\nDetected common title parts (across all items):")
    for idx, w in enumerate(common_words, start=1):
        print(f"{idx}. {w}")

    choice = input(
        "\nChoose word/term number(s) to replace (comma-separated), or press Enter to skip: "
    ).strip()

    if not choice:
        return selected_items

    try:
        indices = [int(x.strip()) for x in choice.split(",") if x.strip()]
        chosen_terms = [common_words[i - 1] for i in indices]
    except Exception:
        print("Invalid choice, skipping replacement.")
        return selected_items

    # ask for replacement for each chosen term
    replacements = {}
    for term in chosen_terms:
        replacement = input(f"Replace '{term}' with (leave empty to skip): ").strip()
        if replacement:
            replacements[term] = replacement

    if not replacements:
        print("No valid replacements provided, skipping.")
        return selected_items

    changed_items = []

    # apply replacements only to selected items
    for item in selected_items:
        original = item["name"]
        new_name = original

        for old, new in replacements.items():
            new_name = new_name.replace(old, new)

        if new_name != original:
            item["name"] = new_name
            changed_items.append(item)

    # only show logs if something changed
    if changed_items:
        print("\nApplied replacements:")
        for old, new in replacements.items():
            print(f"  {old} → {new}")
    else:
        print("\nNo selected items contained the chosen terms. No changes applied.")

    return selected_items

# dashboard JSON export
def export_dashboard_json(metadata):
    # ensure reports directory exists
    REPORTS_DIRECTORY.mkdir(exist_ok=True)

    # find next available filename
    base = REPORTS_DIRECTORY / "dashboard_export"
    counter = 0

    while True:
        suffix = f"_{counter}" if counter > 0 else ""
        path = Path(f"{base}{suffix}.json")
        if not path.exists():
            break
        counter += 1

    # write JSON file
    with path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nDashboard JSON exported to: {path}")
    return path