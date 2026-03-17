from copy import deepcopy
from dhis.api import api_get, api_post


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
