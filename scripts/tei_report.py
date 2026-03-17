from dhis.tei import build_tei
from dhis.report import write_tei

def main():
    program_id = input("Program id: ").strip()
    org_unit = input("OrgUnit id: ").strip()
    start_date = input("Start date of the enrollment (YYYY-MM-DD): ").strip()
    end_date = input("End date of the enrollment (YYYY-MM-DD): ").strip()

    print("\nEnter each dataElement id you want as a column.")
    print("Type '1' when done entering data element.\n")

    column_ids = []
    while True:
        de = input("DataElement id: ").strip()
        if de.lower() == "1":
            break
        if de:
            column_ids.append(de)

    if not column_ids:
        print("No dataElements provided. Exiting.")
        return

    data = build_tei(program_id, org_unit, start_date, end_date, column_ids)
    write_tei(data)

    print("TEI report generated")


if __name__ == "__main__":
    main()
