from urllib.parse import urlencode
from dhis.api import api_get
from dhis.utils import parse_date, compare_dates
from dhis.config import CASE_NUMBER_COLUMN_ID

# Fetching traked entity instance using the API
def fetch_full_teis(program_id, org_unit, start_date, end_date):
    query = {
        "program": program_id,
        "orgUnit": org_unit,
        "ouMode": "DESCENDANTS",
        "fields": (
            "trackedEntity,trackedEntityType,orgUnit,"
            "attributes[attribute,value,displayName],"
            "enrollments[enrollment,program,orgUnit,enrollmentDate,"
            "events[event,eventDate,dataValues[dataElement,value]]]"
        ),
        "enrollmentOccurredAfter": start_date,
        "enrollmentOccurredBefore": end_date,
        "pageSize": "10000",
        "totalPages": "false",
    }

    res = api_get(f"tracker/trackedEntities?{urlencode(query)}")
    # In the new tracker API, TEIs are usually under "instances"
    return res.get("instances", [])

# Data element metadata
def fetch_dataelement_info(de_id):
    meta = api_get(f"dataElements/{de_id}?fields=id,displayName,optionSet[id]")
    return meta.get("displayName", de_id), meta.get("optionSet", {}).get("id")

def fetch_options_for_optionset(optionset_id):
    query = urlencode({
        "fields": "id,code,name",
        "filter": f"optionSet.id:eq:{optionset_id}",
    })
    res = api_get(f"options?{query}")
    return {opt["id"]: opt["name"] for opt in res.get("options", [])}

# Organisation unit fetching
def fetch_org_units_display_names(org_unit_ids):
    if not org_unit_ids:
        return {}

    query = urlencode({
        "fields": "id,displayName",
        "filter": f"id:in:[{','.join(org_unit_ids)}]",
        "paging": "false",
    })

    res = api_get(f"organisationUnits.json?{query}")

    return {
        ou["id"]: ou["displayName"]
        for ou in res.get("organisationUnits", [])
    }

# Extracting data element values
def extract_de_values(tei, column_ids):
    values = {cid: None for cid in column_ids}

    for enr in tei.get("enrollments", []):
        for evt in enr.get("events", []):
            for dv in evt.get("dataValues", []):
                de = dv.get("dataElement")
                if de in values:
                    val = dv.get("value")
                    if val not in ("", None):
                        values[de] = val

    return values

# Fetching each case number value
def fetch_case_number(tei):
    for attr in tei.get("attributes", []):
        if attr.get("attribute") == CASE_NUMBER_COLUMN_ID:
            value = attr.get("value")
            if value not in ("", None):
                return value
    return None

def fetch_case_number_display_name(teis):
    for tei in teis:
        for attr in tei.get("attributes", []):
            if attr.get("attribute") == CASE_NUMBER_COLUMN_ID:
                return attr.get("displayName", "Case Number")
    return "Case Number"

# Builder
def build_tei(program_id, org_unit, start_date, end_date, column_ids):
    teis = fetch_full_teis(program_id, org_unit, start_date, end_date)

    case_column_name = fetch_case_number_display_name(teis)
    org_unit_column_name = "Organisation unit"

    metadata = [case_column_name, org_unit_column_name]

    # Collect unique orgUnit IDs
    org_unit_ids = {
        tei.get("orgUnit")
        for tei in teis
        if tei.get("orgUnit")
    }

    org_unit_map = fetch_org_units_display_names(org_unit_ids)

    # Fetch data element metadata
    option_sets = {}
    for cid in column_ids:
        name, opt_set = fetch_dataelement_info(cid)
        metadata.append(name)
        if opt_set:
            option_sets[cid] = fetch_options_for_optionset(opt_set)

    rows = []

    for tei in teis:
        # New tracker TEI identifier field
        tei_id = tei["trackedEntity"]

        case_number = fetch_case_number(tei)
        org_unit_id = tei.get("orgUnit")
        org_unit_name = org_unit_map.get(org_unit_id)

        values = extract_de_values(tei, column_ids)

        # Safe filtering (does NOT break case numbers)
        if case_number is None and not any(values.values()):
            continue

        resolved = [case_number, org_unit_name]

        # Add data element values
        for cid in column_ids:
            raw = values[cid]
            if cid in option_sets:
                resolved.append(option_sets[cid].get(raw, raw))
            else:
                resolved.append(raw)
        admission = None
        discharge = None
        if len(column_ids) >= 1:
            raw_admission = values.get(column_ids[0])
            if raw_admission:
                admission = parse_date(raw_admission)

        if len(column_ids) >= 2:
            raw_discharge = values.get(column_ids[1])
            if raw_discharge:
                discharge = parse_date(raw_discharge)

        comparison = compare_dates(admission, discharge)

        rows.append({
            "tei_id": tei_id,
            "values": resolved,
            "comparison": comparison,
        })

    # Sorting by admission date
    def sort_key(row):
        if len(column_ids) >= 1:
            raw = row["values"][2] if len(row["values"]) > 2 else None
            d = parse_date(raw) if raw else None
        else:
            d = None
        return (d is None, d)

    rows = sorted(rows, key=sort_key)

    return {
        "column_names": metadata,
        "rows": rows,
    }
