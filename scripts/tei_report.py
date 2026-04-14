from dhis.tei import build_tei
from dhis.report import write_tei
from dhis.api import api_get


def ask_non_empty(prompt):
    while True:
        v = input(prompt).strip()
        if v:
            return v
        print("This field cannot be empty.")


def fetch_program_dataelements(program_id):
    res = api_get(
        f"programs/{program_id}?fields=programStages[programStageDataElements[dataElement[id,name]]]"
    ) or {}

    elements = []

    for stage in res.get("programStages", []):
        for psde in stage.get("programStageDataElements", []):
            de = psde.get("dataElement")
            if de and de.get("id"):
                elements.append({
                    "id": de["id"],
                    "name": de.get("name", de["id"])
                })

    # Remove duplicates (same DE used in multiple stages)
    unique = {}
    for de in elements:
        unique[de["id"]] = de["name"]

    return [{"id": k, "name": v} for k, v in unique.items()]


def main():
    program_id = ask_non_empty("Program id: ")
    org_unit = ask_non_empty("OrgUnit id: ")
    start_date = ask_non_empty("Start date of the enrollment (YYYY-MM-DD): ")
    end_date = ask_non_empty("End date of the enrollment (YYYY-MM-DD): ")

    des = fetch_program_dataelements(program_id)
    if not des:
        print("No data elements found for this program.")
        return

    print("\nAvailable Data Elements:")
    for idx, de in enumerate(des, start=1):
        print(f"{idx}. {de['name']} ({de['id']})")

    print("\nSelect the data elements you want in the report (e.g. 1,2,3) or type 'all' to include every data element.")
    while True:
        choice = input("Your selection: ").strip().lower()

        if choice == "all":
            column_ids = [de["id"] for de in des]
            break

        if "," in choice:
            parts = [p.strip() for p in choice.split(",")]
        else:
            parts = [choice]

        if all(p.isdigit() and 1 <= int(p) <= len(des) for p in parts):
            column_ids = [des[int(p) - 1]["id"] for p in parts]
            break

        print("Invalid selection. Try again.")
    data = build_tei(program_id, org_unit, start_date, end_date, column_ids)

    write_tei(data)
    print("TEI report generated.")


if __name__ == "__main__":
    main()
