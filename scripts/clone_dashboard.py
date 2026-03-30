import json
import copy
import random
import string
from dhis.api import api_get, api_post
from dhis.config import REPORTS_DIRECTORY


def dhis2_uid():
    letters = string.ascii_letters
    chars = string.ascii_letters + string.digits
    return random.choice(letters) + ''.join(random.choice(chars) for _ in range(10))


def clone_dashboard_item(item):
    cloned = copy.deepcopy(item)

    # Remove fields DHIS2 will regenerate
    for field in [
        "id", "uid", "created", "lastUpdated", "href",
        "access", "user", "userGroupAccesses", "userAccesses",
        "favorites", "externalAccess", "attributeValues"
    ]:
        cloned.pop(field, None)

    # Assign new UID
    new_id = dhis2_uid()
    cloned["id"] = new_id
    cloned["uid"] = new_id

    return cloned


def is_dashboard_empty(dashboard):
    items = dashboard.get("dashboardItems", [])
    return len(items) == 0


def get_bottom_y(dashboard_items):
    """
    Determine the bottom-most Y coordinate of existing items.
    """
    bottom = 0
    for item in dashboard_items:
        y = item.get("y", 0)
        h = item.get("height", 1)
        bottom = max(bottom, y + h)
    return bottom


def shift_items_down(items, offset):
    """
    Shift all items downward by a given Y offset.
    """
    for item in items:
        item["y"] = item.get("y", 0) + offset
    return items


def build_cloned_dashboard_metadata(source_dashboard, target_dashboard):
    cloned_items = []

    for item in source_dashboard.get("dashboardItems", []):
        cloned_items.append(clone_dashboard_item(item))

    existing_items = target_dashboard.get("dashboardItems", [])

    # Determine where the existing dashboard ends
    bottom_y = get_bottom_y(existing_items)

    # Shift cloned items so they appear below existing ones
    cloned_items = shift_items_down(cloned_items, bottom_y)

    metadata = {
        "dashboards": [
            {
                "id": target_dashboard["id"],
                "name": target_dashboard["name"],
                "dashboardItems": existing_items + cloned_items
            }
        ]
    }

    return metadata


def main():
    source_id = input("Source dashboard ID: ").strip()
    if not source_id:
        return

    target_id = input("Target dashboard ID: ").strip()
    if not target_id:
        return

    source_dashboard = api_get(f"dashboards/{source_id}.json?fields=*,dashboardItems[*]")
    if source_dashboard is None:
        print("Source dashboard not found.")
        return

    target_dashboard = api_get(f"dashboards/{target_id}.json?fields=*,dashboardItems[*]")
    if target_dashboard is None:
        print("Target dashboard not found.")
        return

    # Warn if destination dashboard is not empty
    if not is_dashboard_empty(target_dashboard):
        print("Warning: The destination dashboard is not empty.")
        choice = input("Do you want to continue and add items to it? (y/n): ").strip().lower()
        if choice != "y":
            print("Operation cancelled.")
            return

    cloned_metadata = build_cloned_dashboard_metadata(source_dashboard, target_dashboard)

    report_path = REPORTS_DIRECTORY / "cloned_dashboard.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(cloned_metadata, f, indent=2)

    api_post("metadata", cloned_metadata)

    print("Done.")
    print(f"Cloned dashboard JSON saved to: {report_path}")


if __name__ == "__main__":
    main()
