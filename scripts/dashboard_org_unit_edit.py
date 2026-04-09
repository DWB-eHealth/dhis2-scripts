from dhis.api import (fetch_object, orgunit_exists, import_object, api_get)
from dhis.dashboard import (replace_item_in_dashboard, clone_object_with_new_ou)
from dhis.utils import detect_and_replace_common_title_parts, export_dashboard_json


def main():
    dashboard_id = input("Enter dashboard ID to edit: ").strip()
    if not dashboard_id:
        return
    dashboard = api_get(
        "dashboards/"
        f"{dashboard_id}.json?fields=id,name,"
        "dashboardItems[id,type,name,"
        "eventReport[id,name,organisationUnits],"
        "visualization[id,name,organisationUnits],"
        "map[id,name,organisationUnits]]"
    )
    if dashboard is None:
        print("Dashboard not found")
        return

    # Extract items
    items = []
    for item in dashboard.get("dashboardItems", []):
        if item.get("type") == "EVENT_REPORT" and item.get("eventReport"):
            items.append({
                "type": "eventReport",
                "collection": "eventReports",
                "id": item["eventReport"]["id"],
                "name": item["eventReport"].get("name", ""),
                "ou": item["eventReport"].get("organisationUnits", [])
            })
        if item.get("type") == "VISUALIZATION" and item.get("visualization"):
            items.append({
                "type": "visualization",
                "collection": "visualizations",
                "id": item["visualization"]["id"],
                "name": item["visualization"].get("name", ""),
                "ou": item["visualization"].get("organisationUnits", [])
            })
        if item.get("type") == "MAP" and item.get("map"):
            items.append({
                "type": "map",
                "collection": "maps",
                "id": item["map"]["id"],
                "name": item["map"].get("name", ""),
                "ou": item["map"].get("organisationUnits", [])
            })

        if not items:
            print("No items found in dashboard")
            return

    # Display items once
    print("\nDashboard items:")
    for idx, it in enumerate(items, start=1):
        print(f"{idx}. [{it['type']}] {it['name']} ({it['id']})")

    # Initialize metadata ONCE
    cloned_metadata = {
    "visualizations": [],
    "maps": [],
    "eventReports": []
    }

    first_run_dashboard_listing = True

    # Main loop for multiple batches
    while True:
        if not first_run_dashboard_listing:
            print("\n----------------------")
            print("\nDashboard items:")
            for idx, it in enumerate(items, start=1):
                print(f"{idx}. [{it['type']}] {it['name']} ({it['id']})")

        first_run_dashboard_listing = False

        choice = input("Select item number(s) or 'all' (or 'exit'): ").strip().lower()
        if choice == "exit":
            break

        if choice == "all":
            selected_items = items.copy()
        else:
            try:
                indices = [int(x.strip()) for x in choice.split(",") if x.strip()]
                selected_items = [items[i - 1] for i in indices]
            except Exception:
                print("Invalid selection")
                continue

        if not selected_items:
            print("No items selected, skipping batch.")
            continue

        # Title replacement
        selected_items = detect_and_replace_common_title_parts(items, selected_items)

        # Org units
        ou_input = input("Enter one or more orgUnit IDs (comma-separated): ").strip()
        if not ou_input:
            print("No org units entered, skipping batch.")
            continue

        new_ou_ids = [x.strip() for x in ou_input.split(",") if x.strip()]
        if not new_ou_ids:
            print("No valid org units parsed, skipping batch.")
            continue

        invalid_ous = [ou for ou in new_ou_ids if not orgunit_exists(ou)]
        if invalid_ous:
            print(f"These org units do not exist: {', '.join(invalid_ous)}")
            print("Batch skipped.")
            continue

        # Process each selected item
        for selected in selected_items:
            collection = selected["collection"]
            old_id = selected["id"]

            print(f"\nProcessing {selected['name']} ({old_id})")

            full_obj = fetch_object(collection, old_id)
            if not full_obj:
                print("Could not fetch object, skipping")
                continue

            if selected["type"] != "eventReport" and ("program" in full_obj or "programStage" in full_obj):
                print(f"Skipping program-based item: {full_obj.get('name', '')}")
                continue

            full_obj["name"] = selected["name"]

            # Clone once
            cloned = clone_object_with_new_ou(full_obj, new_ou_ids[0])

            # Apply ALL org units
            cloned["organisationUnits"] = [{"id": ou} for ou in new_ou_ids]

            response = import_object(collection, cloned)
            if response is None:
                print("Import failed, skipping replacement")
                continue

            replace_item_in_dashboard(dashboard_id, old_id, cloned["id"])

            cloned_metadata[collection].append(cloned)

            print(
                f"Updated dashboard item {old_id} → {cloned['id']} "
                f"with organisationUnits: {new_ou_ids}"
            )

        print("\nBatch complete.")

    # Export final JSON
    export_dashboard_json(cloned_metadata)
    print("\nAll updates done.")


if __name__ == "__main__":
    main()
