from dhis.api import api_get, api_post


def fetch_object(collection, obj_id):
    return api_get(f"{collection}/{obj_id}.json")

def orgunit_exists(ou_id):
    data = api_get(f"organisationUnits/{ou_id}.json?fields=id")
    return data is not None and "id" in data

def clone_object_with_new_ou(obj, new_ou_id):
    cloned = {k: v for k, v in obj.items() if k != "id"}
    cloned["organisationUnits"] = [{"id": new_ou_id}]
    return cloned

def find_new_object_id(collection, original_obj, new_ou_id):
    name = original_obj.get("name", "")
    results = api_get(
        f"{collection}.json?fields=id,name,organisationUnits[id]&filter=name:eq:{name}&paging=false"
    )
    if not results or collection not in results:
        return None
    for o in results[collection]:
        ous = o.get("organisationUnits", [])
        ou_ids = {ou["id"] for ou in ous}
        if ou_ids == {new_ou_id}:
            return o["id"]
    return None

def replace_item_in_dashboard(dashboard_id, item_type, old_id, new_id):
    dashboard = api_get(
        f"""dashboards/{dashboard_id}.json?fields=
        id,
        name,
        dashboardItems[
            id,
            x,
            y,
            width,
            height,
            eventChart[id],
            eventReport[id],
            map[id],
            chart[id],
            reportTable[id]
        ]"""
    )

    if dashboard is None:
        return

    for item in dashboard.get("dashboardItems", []):
        if item_type in item and item[item_type] and item[item_type]["id"] == old_id:
            item[item_type]["id"] = new_id

    metadata = {
        "dashboards": [
            {
                "id": dashboard["id"],
                "name": dashboard["name"],
                "dashboardItems": dashboard["dashboardItems"]
            }
        ]
    }

    api_post("metadata", metadata)

def main():
    dashboard_id = input("Dashboard ID: ").strip()
    if not dashboard_id:
        return

    dashboard = api_get(
        f"dashboards/{dashboard_id}.json?fields=id,name,dashboardItems[id,eventChart[id,name],eventReport[id,name],map[id,name],chart[id,name],reportTable[id,name]]"
    )
    if dashboard is None:
        return

    items = []
    for item in dashboard.get("dashboardItems", []):
        for t in ["eventChart", "eventReport", "map", "chart", "reportTable"]:
            if t in item and item[t]:
                items.append({
                    "type": t,
                    "collection": t + "s",
                    "id": item[t]["id"],
                    "name": item[t].get("name", "")
                })

    if not items:
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
        obj_type = selected["type"]
        collection = selected["collection"]
        old_id = selected["id"]

        full_obj = fetch_object(collection, old_id)
        if not full_obj:
            continue

        cloned = clone_object_with_new_ou(full_obj, new_ou_id)
        api_post("metadata", {collection: [cloned]})

        new_id = find_new_object_id(collection, full_obj, new_ou_id)
        if not new_id:
            continue

        replace_item_in_dashboard(dashboard_id, obj_type, old_id, new_id)

    print("Done.")


if __name__ == "__main__":
    main()
