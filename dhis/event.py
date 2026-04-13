from dhis.api import api_get, api_post

def fetch_event_by_id(event_id):
    fields = (
        "event,program,programStage,orgUnit,occurredAt,status,"
        "enrollment,trackedEntity,"
        "dataValues[dataElement,value]"
    )
    return api_get(f"tracker/events/{event_id}?fields={fields}")

def update_event_value(event, data_element_id, new_value):
    updated_event = {
        "event": event["event"],
        "program": event["program"],
        "programStage": event["programStage"],
        "orgUnit": event["orgUnit"],
        "occurredAt": event["occurredAt"],
        "status": event.get("status", "ACTIVE"),
        "enrollment": event.get("enrollment"),
        "trackedEntity": event.get("trackedEntity"),
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
            updated_event["dataValues"].append({
                "dataElement": dv["dataElement"],
                "value": dv["value"]
            })

    if not found:
        updated_event["dataValues"].append({
            "dataElement": data_element_id,
            "value": new_value
        })

    return updated_event

def push_event_update(updated_event):
    payload = {"events": [updated_event]}
    return api_post("tracker?async=true", payload)
