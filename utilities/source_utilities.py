from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..db import find_all, find_one, update_one


def get_calendar_events(sourceId, calendarId):
    return find_all(current_app.config['EVENT_COLLECTION'], filter={"sourceId": sourceId,
                                                                    "calendarId": calendarId})


def get_event(objectId):
    return find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)})


def update_event(objectId, update):
    try:
        _id = ObjectId(objectId)
    except InvalidId:
        return {}
    updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)},
                              update={
                                  "$set": update
                              })
    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
        print("Update {} fails".format(objectId))


def approve_calendar_db(calendarId):
    updateResult = update_one(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId},
                              update={
                                  "$set": {"status": "approved"}
                              })
    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
        print("Update {} fails".format(objectId))
    # TODO: update all events

def get_calendar_status(calendarId):
    calendar = find_one(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId})
    return calendar['status']

def get_all_calendar_status():
    calendars = find_all(current_app.config['CALENDAR_COLLECTION'], filter={})
    result = {}
    for calendar in calendars:
        result[calendar["calendarId"]] = calendar["status"]
    return result

def update_calendars_status(update, allstatus):
    for calendarId in allstatus.keys():
        if calendarId in update: # approve
            updateResult = update_one(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId},
                                      update={
                                          "$set": {"status": "approved"}
                                      })
            if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                print("Update {} fails".format(calendarId))
        else: # disapprove
            updateResult = update_one(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId},
                                      update={
                                          "$set": {"status": "disapproved"}
                                      })
            if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                print("Update {} fails".format(calendarId))
