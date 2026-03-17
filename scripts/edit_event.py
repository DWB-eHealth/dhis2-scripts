from dhis.report import write_event_xlsx
from dhis.event import fetch_event_by_id, update_event_value, push_event_update


def main():
    org_unit = input("Org unit ID: ").strip()
    data_element_id = input("Data element ID: ").strip()
    event_id = input("Event ID: ").strip()
    condition_value = input("Condition (current value must equal): ").strip()
    new_value = input("New value to set: ").strip()

    print("\nFetching event...")
    event = fetch_event_by_id(event_id)

    if event is None:
        print("Event not found.")
        return

    if event["orgUnit"] != org_unit:
        print(f"Error: Event belongs to orgUnit {event['orgUnit']}, not {org_unit}")
        return

    print(f"Event found: {event['event']}")

    # Find current value
    current_value = None
    for dv in event.get("dataValues", []):
        if dv["dataElement"] == data_element_id:
            current_value = dv["value"]
            break

    print(f"Current value: {current_value}")

    if current_value != condition_value:
        print("Condition not met. No update performed.")
        return

    print("Condition met. Updating event")

    updated_event = update_event_value(event, data_element_id, new_value)

    result = push_event_update(event_id, updated_event)

    print("\nUpdate result:")
    print(result)

    print("\nFetching updated event for verification...")
    updated = fetch_event_by_id(event_id)

    write_event_xlsx(event, updated)

    print("\nDone")


if __name__ == "__main__":
    main()
