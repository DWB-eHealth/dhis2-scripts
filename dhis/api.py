import requests
from dhis.config import DHIS2_BASE_URL, DHIS2_USERNAME, DHIS2_PASSWORD

AUTH = (DHIS2_USERNAME, DHIS2_PASSWORD)

def safe_json(response):
    try:
        return response.json()
    except ValueError:
        print("Invalid JSON response from server.")
        print("Status:", response.status_code)
        print("Body:", response.text[:300])
        raise RuntimeError("Invalid JSON response.")

def api_get(path: str):
    url = f"{DHIS2_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    r = requests.get(url, auth=AUTH)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return safe_json(r)

def api_post(path: str, payload):
    url = f"{DHIS2_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    r = requests.post(url, json=payload, auth=AUTH)
    if r.status_code == 409:
        try:
            print("409 response:", r.json())
        except ValueError:
            print("409 response text:", r.text)
    r.raise_for_status()
    return safe_json(r) if r.text.strip() else {}


def api_put(path: str, payload):
    url = f"{DHIS2_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    r = requests.put(url, json=payload, auth=AUTH)
    r.raise_for_status()
    return safe_json(r) if r.text.strip() else {}


# Dashboard related functions
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

# import cloned metadata into DHIS2
def import_object(collection, cloned):
    # import cloned metadata into DHIS2
    try:
        return api_post("metadata", {collection: [cloned]})
    except Exception as e:
        print(f"Error importing {collection[:-1]} {cloned.get('name', '')}: {e}")
        return None