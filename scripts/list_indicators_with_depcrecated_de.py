import re
from urllib.parse import quote

from dhis.api import api_get
from dhis.report import write_indicator_deprecated_deg_excel


def ask_choice(prompt, max_index):
    while True:
        v = input(prompt).strip()
        if v.isdigit():
            i = int(v)
            if 1 <= i <= max_index:
                return i
        print("Invalid selection. Type a number from the list.")


def fetch_data_element_groups():
    res = api_get(
        "dataElementGroups?fields=id,name&paging=false"
    ) or {}
    return res.get("dataElementGroups", [])


def fetch_data_elements_in_group(deg_id):
    res = api_get(
        f"dataElementGroups/{deg_id}?fields=dataElements[id,name]&paging=false"
    ) or {}
    des = res.get("dataElements", []) or []
    return {de["id"] for de in des if "id" in de}


def fetch_indicators():
    # Need numerator, denominator, and indicatorGroups to match by name
    query = (
        "indicators?"
        "fields=id,code,name,"
        "indicatorGroups[id,name],"
        "numerator,denominator"
        "&paging=false"
    )
    res = api_get(query) or {}
    return res.get("indicators", [])


def extract_de_ids_from_expression(expr):
    if not expr:
        return []
    # Matches {deId} patterns
    return re.findall(r"{(.*?)}", expr)


def describe_expression(expr):
    if not expr:
        return ""
    res = api_get(
        f"expressions/description?expression={quote(expr, safe='')}"
    ) or {}
    return res.get("description", "")


def build_rows_for_group(group_name, group_de_ids, indicators):
    rows = []

    for ind in indicators:
        # Only consider indicators that belong to the indicator group
        ind_groups = ind.get("indicatorGroups", []) or []
        ind_group_names = {g.get("name", "") for g in ind_groups}
        if group_name not in ind_group_names:
            continue

        numerator = ind.get("numerator", "")
        denominator = ind.get("denominator", "")

        num_des = set(extract_de_ids_from_expression(numerator))
        den_des = set(extract_de_ids_from_expression(denominator))
        all_des = num_des | den_des

        # Check if any DE in this indicator is part of the chosen DEG
        if not (all_des & group_de_ids):
            continue

        num_desc = describe_expression(numerator)
        den_desc = describe_expression(denominator)

        rows.append({
            "group_name": group_name,
            "name": ind.get("name", ""),
            "code": ind.get("code", ""),
            "numerator": num_desc,
            "denominator": den_desc,
        })

    return rows


def main():
    print("Fetching data element groups…")
    degs = fetch_data_element_groups()
    if not degs:
        print("No data element groups found.")
        return

    print("\nAvailable Data Element Groups:")
    for idx, deg in enumerate(degs, start=1):
        print(f"{idx}. {deg['name']} ({deg['id']})")

    choice = ask_choice("\nSelect a data element group by number: ", len(degs))
    chosen_deg = degs[choice - 1]
    group_id = chosen_deg["id"]
    group_name = chosen_deg["name"]

    print(f"\nSelected group: {group_name} ({group_id})")

    print("Fetching data elements in this group…")
    group_de_ids = fetch_data_elements_in_group(group_id)
    if not group_de_ids:
        print("No data elements in this group.")
        return

    print("Fetching indicators…")
    indicators = fetch_indicators()
    print(f"Total indicators: {len(indicators)}")

    print("Checking indicators for use of this group's data elements…")
    rows = build_rows_for_group(group_name, group_de_ids, indicators)

    if not rows:
        print("No indicators found using data elements from this group.")
        return

    print(f"Found {len(rows)} indicators. Writing Excel report in ./reports …")
    write_indicator_deprecated_deg_excel(rows)
    print("Done.")


if __name__ == "__main__":
    main()
