from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..db import find_all, find_one, update_one 


def get_calendar_events(sourceId, calendarId):
    return find_all(current_app.config['EVENT_COLLECTION'], filter={"sourceId": sourceId, 
                                                                    "calendarId": calendarId})

