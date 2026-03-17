import json
from copy import deepcopy
from dhis.api import api_get, api_post
from dhis.config import REPORTS_DIRECTORY

def clean_dashboard_item(item):
    cleaned = deepcopy(item)
    # Fields to strip for clean cloning
    fields_to_remove = {
        "id", "href", "created", "lastUpdated", "access", "favorite",
        "interpretationCount", "interpretationLikeCount", "externalAccess",
        "userGroupAccesses", "userAccesses", "users", "favorites",
        "reports", "resources", "translations", "attributeValues"
    }
    for field in fields_to_remove:
        cleaned.pop(field, None)
    return cleaned

def build_cloned_dashboard_metadata(source_dashboard, target_dashboard):
    cloned_items = [
        clean_dashboard_item(item)
        for item in source_dashboard.get("dashboardItems", [])
    ]
    metadata = {
        "dashboards": [
            {
                "id": target_dashboard["id"],
                "name": target_dashboard["name"],
                "dashboardItems": cloned_items
            }
        ]
    }
    return metadata

def main():
    source_id = input("Source dashboard ID: ").strip()
    if not source_id:
        print("Source ID cannot be empty.")
        return

    target_id = input("Target dashboard ID: ").strip()
    if not target_id:
        print("Target ID cannot be empty.")
        return

    print(f"\nFetching source dashboard {source_id}...")
    source_dashboard = api_get(f"dashboards/{source_id}.json")
    if source_dashboard is None:
        print("Source dashboard not found.")
        return

    print(f"Fetching target dashboard {target_id}...")
    target_dashboard = api_get(f"dashboards/{target_id}.json")
    if target_dashboard is None:
        print("Target dashboard not found.")
        return

    print("Building cloned metadata...")
    cloned_metadata = build_cloned_dashboard_metadata(source_dashboard, target_dashboard)

    # Saving dashboard
    report_path = REPORTS_DIRECTORY / "cloned_dashboard.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(cloned_metadata, f, indent=2)

    print(f"Preview saved: {report_path}")

    print("\nApplying changes to target dashboard...")
    result = api_post("metadata", cloned_metadata)

    print("\nImport result:")
    print(json.dumps(result, indent=2))
    print("\nDone!")
    print(f"Preview file: {report_path}")


if __name__ == "__main__":
    main()
