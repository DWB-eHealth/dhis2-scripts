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
    r.raise_for_status()
    return safe_json(r) if r.text.strip() else {}

def api_put(path: str, payload):
    url = f"{DHIS2_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    r = requests.put(url, json=payload, auth=AUTH)
    r.raise_for_status()
    return safe_json(r) if r.text.strip() else {}
