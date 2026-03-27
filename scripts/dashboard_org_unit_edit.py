import random
import string
import json
from collections import Counter
from pathlib import Path
from dhis.api import api_get, api_post

REPORTS_DIRECTORY = Path("reports")

# uid generator
def dhis2_uid():
    # generate a DHIS2‑compatible UID
    letters = string.ascii_letters
    chars = string.ascii_letters + string.digits
    return random.choice(letters) + ''.join(random.choice(chars) for _ in range(10))


# fetch full metadata object without access/user fields
def fetch_object(collection, obj_id):
    # fetch full metadata object without access/user fields
    return api_get(
        f"{collection}/{obj_id}.json?fields=*,!access,!user,!userGroupAccesses,!userAccesses,!favorites,!href,!lastUpdatedBy,!createdBy"
    )

# organisation unit existence check
def orgunit_exists(ou_id):
    # verify orgUnit exists before cloning
    data = api_get(f"organisationUnits/{ou_id}.json?fields=id")
    return data is not None and "id" in data


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


# clone metadata object with new UID and orgUnit
def clone_object_with_new_ou(obj, new_ou_id):
    # clone metadata object with new UID and orgUnit
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


# import cloned metadata into DHIS2
def import_object(collection, cloned):
    # import cloned metadata into DHIS2
    try:
        return api_post("metadata", {collection: [cloned]})
    except Exception as e:
        print(f"Error importing {collection[:-1]} {cloned.get('name', '')}: {e}")
        return None


# replace old item ID with new item ID in dashboard configuration
def replace_item_in_dashboard(dashboard_id, old_id, new_id):
    # update dashboard to point to cloned item
    dashboard = api_get(
        f"dashboards/{dashboard_id}.json?fields=id,name,dashboardItems[*]"
    )
    if dashboard is None:
        print("Could not load dashboard for replacement")
        return

    for item in dashboard.get("dashboardItems", []):
        if item.get("visualization", {}).get("id") == old_id:
            item["visualization"]["id"] = new_id
        if item.get("map", {}).get("id") == old_id:
            item["map"]["id"] = new_id

    api_post("metadata", {
        "dashboards": [{
            "id": dashboard["id"],
            "name": dashboard["name"],
            "dashboardItems": dashboard["dashboardItems"]
        }]
    })


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


def main():
    dashboard_id = input("Dashboard ID: ").strip()
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

    choice = input("Choose item number(s) or 'all': ").strip().lower()
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

        print(f"\n➡ Processing {selected['name']} ({old_id})")

        full_obj = fetch_object(collection, old_id)
        if not full_obj:
            print("Could not fetch object, skipping")
            continue

        # skip if orgUnit already matches
        existing_ous = [ou["id"] for ou in full_obj.get("organisationUnits", [])]
        if new_ou_id in existing_ous:
            print("⚠ Skipping: item already uses this orgUnit.")
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

    print("\nDone.")


if __name__ == "__main__":
    main()
