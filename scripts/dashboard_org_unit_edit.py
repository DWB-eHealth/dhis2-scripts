from dhis.api import (
    fetch_object, orgunit_exists, import_object,api_get
)
from dhis.dashboard import (
    replace_item_in_dashboard, clone_object_with_new_ou
)
from dhis.utils import detect_and_replace_common_title_parts, export_dashboard_json

def main():
    dashboard_id = input("Enter dashboard ID to edit: ").strip()
    if not dashboard_id:
        return

    dashboard = api_get(
        "dashboards/"
        f"{dashboard_id}.json?fields=id,name,"
        "dashboardItems[id,type,name,"
        "visualization[id,name,organisationUnits],"
        "map[id,name,organisationUnits]]"
    )
    if dashboard is None:
        print("Dashboard not found")
        return

    # extract items
    items = []
    for item in dashboard.get("dashboardItems", []):
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

    # display items
    for idx, it in enumerate(items, start=1):
        print(f"{idx}. [{it['type']}] {it['name']} ({it['id']})")

    choice = input("Select item by number(s) or 'all': ").strip().lower()
    if choice == "all":
        selected_items = items.copy()
    else:
        indices = [int(x.strip()) for x in choice.split(",")]
        selected_items = [items[i - 1] for i in indices]

    # title replacement step
    selected_items = detect_and_replace_common_title_parts(items, selected_items)

    new_ou_id = input("New orgUnit ID: ").strip()
    if not new_ou_id:
        return

    if not orgunit_exists(new_ou_id):
        print("OrgUnit does not exist.")
        return

    cloned_metadata = {"visualizations": [], "maps": []}

    # process each selected item
    for selected in selected_items:
        collection = selected["collection"]
        old_id = selected["id"]

        print(f"\nProcessing {selected['name']} ({old_id})")

        full_obj = fetch_object(collection, old_id)
        if not full_obj:
            print("Could not fetch object, skipping")
            continue

        # skip if orgUnit already matches
        existing_ous = [ou["id"] for ou in full_obj.get("organisationUnits", [])]
        if new_ou_id in existing_ous:
            print("Skipping: item already uses this orgUnit.")
            continue

        # skip program-based items
        if "program" in full_obj or "programStage" in full_obj:
            print(f"Skipping program-based item: {full_obj.get('name', '')}")
            continue

        # apply updated title
        full_obj["name"] = selected["name"]

        cloned = clone_object_with_new_ou(full_obj, new_ou_id)

        response = import_object(collection, cloned)
        if response is None:
            print("Import failed, skipping replacement")
            continue

        replace_item_in_dashboard(dashboard_id, old_id, cloned["id"])

        cloned_metadata[collection].append(cloned)

        print(f"Updated dashboard item {old_id} → {cloned['id']}")

    # export final JSON
    export_dashboard_json(cloned_metadata)
    print("\nUpdate done.")

if __name__ == "__main__":
    main()
