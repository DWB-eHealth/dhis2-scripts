from dhis.api import api_get
from dhis.report import write_indicator_group_excel

def fetch_indicators():
    query = (
        "indicators?"
        "fields=id,code,name,"
        "indicatorType[id,name],"
        "indicatorGroups[id,name]"
        "&paging=false"
    )

    res = api_get(query) or {}
    return res.get("indicators", [])

def build_rows(indicators):
    rows = []

    for ind in indicators:
        ind_id = ind.get("id", "")
        code = ind.get("code", "")
        name = ind.get("name", "")

        ind_type = ""
        if ind.get("indicatorType"):
            ind_type = ind["indicatorType"].get("name", "")

        groups = ind.get("indicatorGroups", []) or []
        group_names = ", ".join(g.get("name", "") for g in groups) if groups else ""

        rows.append({
            "indicator_group": group_names,
            "indicator_type": ind_type,
            "name": name,
            "id": ind_id,
            "code": code,
        })

    return rows

def main():
    print("Fetching indicators from DHIS2…")
    indicators = fetch_indicators()
    print(f"Retrieved {len(indicators)} indicators.")
    print("Building rows…")
    rows = build_rows(indicators)
    write_indicator_group_excel(rows)
    print("Done.")
if __name__ == "__main__":
    main()
