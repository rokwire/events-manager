import json
import datetime
import requests
import traceback

from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..db import find_all, find_one, update_one, update_many

# find many events in a calendar with selected status
def get_calendar_events(sourceId, calendarId, select_status):
    if not select_status:
        select_status = ['pending']
    print(select_status)
    return list(find_all(current_app.config['EVENT_COLLECTION'], filter={"sourceId": sourceId,
                                                                    "calendarId": calendarId,
                                                                    "eventStatus": {"$in": select_status} }))

# find the count of events in a calendar with selected status
def get_calendar_events_count(sourceId, calendarId, select_status):
    pass

# find many events in a calendar with selected status with pagination
def get_calendar_events_pagination(sourceId, calendarId, select_status, skip, limit):
    pass

# Approve events from a calendar
def approve_calendar_events(calendarId):
    updateResult = update_many(current_app.config['EVENT_COLLECTION'], condition={"calendarId": calendarId}, update={
        "$set": {"eventStatus": "approved"}
    })
    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
        print("approve calendar {} fails in approve_calendar_events".format(calendarId))

# Disapprove events from a calendar
def disapprove_calendar_events(calendarId):
    updateResult = update_many(current_app.config['EVENT_COLLECTION'], condition={"calendarId": calendarId}, update={
        "$set": {"eventStatus": "disapproved"}
    })
    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
        print("approve calendar {} fails in approve_calendar_events".format(calendarId))


def publish_event(id):
    headers = {'Content-Type': 'application/json'}
    try:
        event = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)},
                         projection={'_id': 0, 'eventStatus': 0})

        if event:
            print("event {} submit method: {}".format(id, event['submitType']))
            if event.get('startDate'):
                event['startDate'] = datetime.datetime.strptime(event['startDate'], "%Y-%m-%dT%H:%M:%S")
                event['startDate'] = event['startDate'].strftime("%Y/%m/%dT%H:%M:%S")
            if event.get('endDate'):
                event['endDate'] = datetime.datetime.strptime(event['endDate'], "%Y-%m-%dT%H:%M:%S")
                event['endDate'] = event['endDate'].strftime("%Y/%m/%dT%H:%M:%S")
            submit_type = event['submitType']
            del event['submitType']
            if submit_type == 'post':
                result = requests.post(current_app.config['EVENT_BUILDING_BLOCK_URL'], headers=headers,
                                       data=json.dumps(event))
            elif submit_type == 'put':
                url = current_app.config['EVENT_BUILDING_BLOCK_URL'] + '/' + event.get('eventId')
                result = requests.put(url, headers=headers,
                                      data=json.dumps(event))
            elif submit_type == 'patch':
                url = current_app.config['EVENT_BUILDING_BLOCK_URL'] + '/' + event.get('eventId')
                result = requests.patch(url, headers=headers,
                                        data=json.dumps(event))

            if result.status_code not in (200, 201):
                print("Event {} submission fails".format(id))
                return False
            else:
                updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)}, update={
                    "$set": {"eventStatus": "published"}
                })
                if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                    print("Publish event {} fails in publish_event".format(id))

                return True


    except Exception:
        traceback.print_exc()
        return False


def approve_event(id):
    print("{} is going to be approved".format(id))
    updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)}, update={
        "$set": {"eventStatus":  "approved"}
    })
    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
        print("Approve event {} fails in approve_event".format(id))

    publish_event(id)


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
        print("Update {} fails in update_event".format(objectId))

# Approve a calendar and relevant events
def approve_calendar_db(calendarId):
    updateResult = update_one(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId},
                              update={
                                  "$set": {"status": "approved"}
                              }, upsert=True)
    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
        print("Update {} fails".format(objectId))
    approve_calendar_events(calendarId)

# Disapprove a calendar and relevant events
def disapprove_calendar_db(calendarId):
    updateResult = update_one(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId},
                              update={
                                  "$set": {"status": "disapproved"}
                              }, upsert=True)
    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
        print("Update {} fails".format(objectId))
    disapprove_calendar_events(calendarId)

# Find the approval status for one calendar
def get_calendar_status(calendarId):
    calendar = find_one(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId})
    if calendar is None:
        return "disapproved"
    return calendar['status']

# Find the approval status for many calendars
def get_all_calendar_status():
    calendars = find_all(current_app.config['CALENDAR_COLLECTION'], filter={})
    result = {}
    for dict in current_app.config['INT2CAL']:
        for calendarId, name in dict.items():
            calendar = find_one(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId})
            # print(calendar)
            if calendar is not None:
                result[calendarId] = calendar["status"]
            else:
                result[calendarId] = "disapproved"
    return result

# Update approval status for many calendars (and relevant events)
def update_calendars_status(update, allstatus):
    for calendarId in allstatus.keys():
        if calendarId in update: # approve
            approve_calendar_db(calendarId)
        else: # disapprove
            disapprove_calendar_db(calendarId)

# Find the approval status for one calendar event
def get_calendar_event_status(id):
    pass

# disapprove a calendar event
def disapprove_event(id):
    pass
