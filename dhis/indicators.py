from .api import api_get
from .utils import extract_uids_from_expression

variable_types = [
    "dataElements",
    "programDataElements",
    "categoryOptionCombos",
    "indicators",
    "dataSets",
    "programs",
]

def get_name_for_uid(uid):
    meta = api_get(f"metadata.json?filter=id:eq:{uid}&fields=:all")
    if not meta or not meta.get("metadata"):
        return None

    md = meta["metadata"]
    for key in variable_types:
        if key in md and md[key]:
            return md[key][0].get("name")
    return None

def categorize_uids(uids):
    categories = {k: [] for k in variable_types}
    names = {k: [] for k in variable_types}

    for uid in uids:
        meta = api_get(f"metadata.json?filter=id:eq:{uid}&fields=:all")
        if not meta or not meta.get("metadata"):
            continue

        md = meta["metadata"]
        for key in categories.keys():
            if key in md and md[key]:
                categories[key].append(uid)
                names[key].append(md[key][0].get("name"))

    return categories, names

def process_indicator(indicator_id: str):
    indicator = api_get(f"indicators/{indicator_id}.json")
    if indicator is None:
        return None

    numerator = indicator.get("numerator", "")
    denominator = indicator.get("denominator", "")
    numerator_description = indicator.get("numeratorDescription", "")
    denominator_description = indicator.get("denominatorDescription", "")

    numerator_uids = extract_uids_from_expression(numerator)
    denominator_uids = extract_uids_from_expression(denominator)

    numerator_refs_ids, numerator_refs_names = categorize_uids(numerator_uids)
    denominator_refs_ids, denominator_refs_names = categorize_uids(denominator_uids)

    return {
        "uid": indicator_id,
        "name": indicator.get("name", ""),
        "numerator": numerator,
        "numeratorDescription": numerator_description,
        "numeratorRefsIDs": numerator_refs_ids,
        "numeratorRefsNames": numerator_refs_names,
        "denominator": denominator,
        "denominatorDescription": denominator_description,
        "denominatorRefsIDs": denominator_refs_ids,
        "denominatorRefsNames": denominator_refs_names,
    }
