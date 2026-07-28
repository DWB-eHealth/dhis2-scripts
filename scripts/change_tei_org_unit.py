from dhis.api import api_get, api_post, api_put
from dhis.tei import fetch_org_units_display_names

def fetch_tei(tei_id: str):
    path = (
        f"tracker/trackedEntities/{tei_id}"
        "?fields=trackedEntity,trackedEntityType,orgUnit,"
        "enrollments[enrollment,program,orgUnit,status,enrolledAt]"
    )
    return api_get(path)

def find_enrollment(tei, program_id):
    for enr in tei.get("enrollments", []):
        if enr["program"] == program_id:
            return enr
    return None

def fetch_tei_events(tei_id, program_id):
    path = (
        f"tracker/events?"
        f"trackedEntity={tei_id}&program={program_id}"
        "&fields=event,programStage,orgUnit,occurredAt,enrollment"
    )
    res = api_get(path) or {}
    return res.get("events", [])

def format_event(evt, org_unit_map):
    parts = []
    for key, value in evt.items():
        if key == "orgUnit":
            name = org_unit_map.get(value, value)
            parts.append(f"{key}: {name}")
        else:
            parts.append(f"{key}: {value}")
    return " | ".join(parts)


def select_event(events):
    # Collect all orgUnit IDs from events
    ou_ids = {evt.get("orgUnit") for evt in events if evt.get("orgUnit")}
    org_unit_map = fetch_org_units_display_names(list(ou_ids))

    print("\nAvailable events:")
    for i, evt in enumerate(events, start=1):
        print(f"{i}. {format_event(evt, org_unit_map)}")

    while True:
        choice = input("\nSelect event number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(events):
            return events[int(choice) - 1]
        print("Invalid choice.")


def update_event(event, new_ou):
    payload = {
        "events": [
            {
                "event": event["event"],
                "programStage": event["programStage"],
                "enrollment": event["enrollment"],
                "orgUnit": new_ou,
                "occurredAt": event["occurredAt"]
            }
        ]
    }

    return api_post("tracker?async=false", payload)


def move_tei_registration_ou(tei, new_ou):
    payload = {
        "trackedEntities": [
            {
                "trackedEntity": tei["trackedEntity"],
                "trackedEntityType": tei["trackedEntityType"],
                "orgUnit": new_ou
            }
        ]
    }
    return api_post("tracker?async=false", payload)


def transfer_ownership(tei_id, program_id, new_ou):
    path = (
        f"tracker/ownership/transfer"
        f"?trackedEntity={tei_id}"
        f"&program={program_id}"
        f"&orgUnit={new_ou}"
    )
    return api_put(path, None)


def main():
    tei_id = input("Enter TEI ID: ").strip()
    tei = fetch_tei(tei_id)
    if not tei:
        print("TEI not found.")
        return

    program_id = input("Enter program ID: ").strip()
    new_ou = input("Enter new organisation unit ID: ").strip()

    # Validate OU
    if not fetch_org_units_display_names([new_ou]).get(new_ou):
        print("Invalid orgUnit.")
        return

    # Validate enrollment
    enrollment = find_enrollment(tei, program_id)
    if not enrollment or enrollment["status"] != "ACTIVE":
        print("Enrollment missing or not active.")
        return

    # Validate program OU assignment
    program = api_get(f"programs/{program_id}?fields=organisationUnits[id]")
    assigned_ous = {ou["id"] for ou in program.get("organisationUnits", [])}
    if new_ou not in assigned_ous:
        print("New orgUnit not assigned to program.")
        return

    # Fetch events
    events = fetch_tei_events(tei_id, program_id)
    if not events:
        print("No events found.")
        return

    # Select event
    event = select_event(events)

    # Update event (orgUnit only)
    update_event(event, new_ou)

    # Update TEI registration OU
    move_tei_registration_ou(tei, new_ou)

    # Transfer ownership
    transfer_ownership(tei_id, program_id, new_ou)

    print("\nDone.")


if __name__ == "__main__":
    main()
