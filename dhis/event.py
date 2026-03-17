from dhis.api import api_get, api_put

def fetch_event_by_id(event_id):
    fields = (
        "event,program,programStage,orgUnit,eventDate,status,"
        "dataValues[dataElement,value]"
    )
    return api_get(f"events/{event_id}.json?fields={fields}")

def update_event_value(event, data_element_id, new_value):
    updated_event = {
        "event": event["event"],
        "program": event["program"],
        "programStage": event["programStage"],
        "orgUnit": event["orgUnit"],
        "eventDate": event["eventDate"],
        "status": event.get("status", "ACTIVE"),
        "dataValues": []
    }

    found = False

    for dv in event.get("dataValues", []):
        if dv["dataElement"] == data_element_id:
            updated_event["dataValues"].append({
                "dataElement": data_element_id,
                "value": new_value
            })
            found = True
        else:
            updated_event["dataValues"].append(dv)

    if not found:
        updated_event["dataValues"].append({
            "dataElement": data_element_id,
            "value": new_value
        })

    return updated_event

def push_event_update(event_id, updated_event):
    return api_put(f"events/{event_id}", updated_event)
