from copy import deepcopy

from dhis.report import write_event_xlsx
from dhis.event import (
    fetch_event_by_id,
    fetch_data_element,
    fetch_option_set,
    update_event_value,
    push_event_update,
)

def ask_non_empty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")

def ask_confirmation(prompt):
    while True:
        ans = input(prompt + " (y/n): ").strip().lower()
        if ans in ("y", "n"):
            return ans == "y"
        print("Please type 'y' or 'n'.")

def build_enriched_list(event):
    enriched = []
    data_values = event.get("dataValues", [])

    for dv in data_values:
        de = fetch_data_element(dv["dataElement"])
        option_set_meta = de.get("optionSet")

        display_value = dv["value"]

        if option_set_meta:
            option_set = fetch_option_set(option_set_meta["id"])
            options = option_set.get("options", [])
            match = next((o for o in options if o["code"] == dv["value"]), None)
            if match:
                display_value = match["name"]

        enriched.append({
            "dataElement": dv["dataElement"],
            "value": dv["value"],
            "displayValue": display_value,
            "name": de.get("name", dv["dataElement"]),
            "optionSet": option_set_meta
        })

    return enriched

def main():
    event_id = ask_non_empty("Event ID: ")

    event = fetch_event_by_id(event_id)
    if not event:
        print("Event not found.")
        return

    if isinstance(event, list):
        if not event:
            print("Event not found.")
            return
        event = event[0]

    # Keep an immutable copy for the report
    original_event = deepcopy(event)

    enriched = build_enriched_list(event)

    if not enriched:
        print("This event has no data values.")
        return

    while True:
        print("\nData Elements for this event")
        for idx, item in enumerate(enriched, start=1):
            print(f"{idx}. {item['name']} : {item['displayValue']}")

        while True:
            choice = input("\nChoose a data element number to edit: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(enriched):
                choice = int(choice)
                break
            print("Invalid number. Try again.")

        selected = enriched[choice - 1]
        de_id = selected["dataElement"]
        current_value = selected["displayValue"]

        print(f"\nSelected: {selected['name']}")
        print(f"Current value: {current_value}")

        option_set = None
        if selected["optionSet"]:
            option_set = fetch_option_set(selected["optionSet"]["id"])

        if option_set:
            print("\nThis data element uses an option set:")
            options = option_set["options"]

            for idx, opt in enumerate(options, start=1):
                print(f"{idx}. {opt['name']} (code: {opt['code']})")

            while True:
                opt_choice = input("Choose an option number: ").strip()
                if opt_choice.isdigit() and 1 <= int(opt_choice) <= len(options):
                    new_value = options[int(opt_choice) - 1]["code"]
                    new_display = options[int(opt_choice) - 1]["name"]
                    break
                print("Invalid number. Try again.")
        else:
            new_value = ask_non_empty("New value: ")
            new_display = new_value

        print(f"\nYou are about to change '{current_value}' → '{new_display}'")
        if not ask_confirmation("Are you sure"):
            print("Change cancelled.")
        else:
            updated_event = update_event_value(event, de_id, new_value)
            push_event_update(updated_event)

            print("Value updated successfully.")

            event = fetch_event_by_id(event_id)
            if isinstance(event, list) and event:
                event = event[0]

            enriched = build_enriched_list(event)

        if not ask_confirmation("\nDo you want to edit another element"):
            break

    final_event = fetch_event_by_id(event_id)
    if isinstance(final_event, list) and final_event:
        final_event = final_event[0]

    write_event_xlsx(original_event, final_event)
    print("\nAll done. XLSX written.")

if __name__ == "__main__":
    main()
