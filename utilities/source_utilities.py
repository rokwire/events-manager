from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..db import find_all, find_one, update_one


def get_calendar_events(sourceId, calendarId, select_status):
    if not select_status:
        select_status = ['pending']
    print(select_status)
    return list(find_all(current_app.config['EVENT_COLLECTION'], filter={"sourceId": sourceId,
                                                                    "calendarId": calendarId,
                                                                    "eventStatus": {"$in": select_status} }))        


def approve_event(id):
    print("{} is going to be approved".format(id))
    return update_one(current_app.config['EVENT_COLLECTION'], condition={"id": ObjectId(id), "update": {
        "eventStatus": {"$set": "approved"}
    }})
    