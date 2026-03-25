import random
import string
from dhis.api import api_get, api_post

def dhis2_uid():
    letters = string.ascii_letters
    chars = string.ascii_letters + string.digits
    return random.choice(letters) + ''.join(random.choice(chars) for _ in range(10))

def fetch_object(collection, obj_id):
    return api_get(
        f"{collection}/{obj_id}.json?fields=*,!access,!user,!userGroupAccesses,!userAccesses,!favorites,!href,!lastUpdatedBy,!createdBy"
    )

def orgunit_exists(ou_id):
    data = api_get(f"organisationUnits/{ou_id}.json?fields=id")
    return data is not None and "id" in data

def clone_object_with_new_ou(obj, new_ou_id):
    cloned = {}
    for k, v in obj.items():
        if k not in [
            "id", "uid", "created", "lastUpdated", "href",
            "lastUpdatedBy", "createdBy", "access",
            "user", "userGroupAccesses", "userAccesses", "favorites"
        ]:
            cloned[k] = v

    new_id = dhis2_uid()
    cloned["id"] = new_id
    cloned["uid"] = new_id
    cloned["organisationUnits"] = [{"id": new_ou_id}]
    return cloned

def import_object(collection, cloned):
    try:
        response = api_post("metadata", {collection: [cloned]})
        return response
    except Exception as e:
        print(f"Error importing {collection[:-1]} {cloned.get('name', '')}: {e}")
        return None

def replace_item_in_dashboard(dashboard_id, old_id, new_id):
    # Fetch full dashboard items to ensure we have the correct structure for update
    dashboard = api_get(
        f"dashboards/{dashboard_id}.json?fields=id,name,dashboardItems[*]"
    )
    if dashboard is None:
        print("Could not load dashboard for replacement")
        return

    for item in dashboard.get("dashboardItems", []):
        # Update only the changed item
        if item.get("visualization", {}).get("id") == old_id:
            item["visualization"]["id"] = new_id

        if item.get("map", {}).get("id") == old_id:
            item["map"]["id"] = new_id

    # Post full dashboard back
    api_post("metadata", {
        "dashboards": [{
            "id": dashboard["id"],
            "name": dashboard["name"],
            "dashboardItems": dashboard["dashboardItems"]
        }]
    })

def main():
    dashboard_id = input("Dashboard ID: ").strip()
    if not dashboard_id:
        return

    dashboard = api_get(
        f"dashboards/{dashboard_id}.json?fields=id,name,dashboardItems[id,type,name,visualization[id,name],map[id,name]]"
    )
    if dashboard is None:
        print("Dashboard not found")
        return

    items = []
    for item in dashboard.get("dashboardItems", []):
        if item.get("type") == "VISUALIZATION" and item.get("visualization"):
            items.append({
                "type": "visualization",
                "collection": "visualizations",
                "id": item["visualization"]["id"],
                "name": item["visualization"].get("name", "")
            })
        if item.get("type") == "MAP" and item.get("map"):
            items.append({
                "type": "map",
                "collection": "maps",
                "id": item["map"]["id"],
                "name": item["map"].get("name", "")
            })

    if not items:
        print("No items found in dashboard")
        return

    for idx, it in enumerate(items, start=1):
        print(f"{idx}. [{it['type']}] {it['name']} ({it['id']})")

    choice = input("Choose item number(s) or 'all': ").strip().lower()
    if choice == "all":
        selected_items = items
    else:
        indices = [int(x.strip()) for x in choice.split(",")]
        selected_items = [items[i - 1] for i in indices]

    new_ou_id = input("New orgUnit ID: ").strip()
    if not new_ou_id:
        return

    if not orgunit_exists(new_ou_id):
        print("OrgUnit does not exist.")
        return

    for selected in selected_items:
        collection = selected["collection"]
        old_id = selected["id"]

        print(f"\n➡ Processing {selected['name']} ({old_id})")

        full_obj = fetch_object(collection, old_id)
        if not full_obj:
            print("Could not fetch object, skipping")
            continue

        if "program" in full_obj or "programStage" in full_obj:
            print(f"Skipping program-based visualization/map: {full_obj.get('name', '')}")
            continue

        cloned = clone_object_with_new_ou(full_obj, new_ou_id)

        response = import_object(collection, cloned)
        if response is None:
            print("Import failed, skipping replacement")
            continue

        replace_item_in_dashboard(dashboard_id, old_id, cloned["id"])
        print(f"Updated dashboard item {old_id} → {cloned['id']}")

    print("\nDone.")

if __name__ == "__main__":
    main()
