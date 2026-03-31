from copy import deepcopy
from dhis.api import api_get, api_post
from dhis.utils import dhis2_uid

def fetch_dashboard(dashboard_id):
    return api_get(f"dashboards/{dashboard_id}.json")

def clean_dashboard_item(item):
    cleaned = deepcopy(item)

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

def push_dashboard_clone(metadata):
    return api_post("metadata", metadata)

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