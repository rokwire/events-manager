from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..db import find_all, find_one, update_one, find_distinct, insert_one

def get_all_user_events(select_status):

    eventIds = find_distinct(current_app.config['EVENT_COLLECTION'], key="eventId",
                             condition={"sourceId": {"$exists": False},
                                        "eventStatus": {"$in": select_status}})
    events_by_eventId = {}
    for eventId in eventIds:
        events = list(find_all(current_app.config['EVENT_COLLECTION'],
                               filter={"eventId": eventId,
                                       "eventStatus": {"$in": select_status}}))

        if events:
            events_by_eventId[eventId] = events

    return events_by_eventId

    # return find_all(current_app.config['EVENT_COLLECTION'], filter={"sourceId": {"$exists": False},
    #                                                                 "eventStatus": {"$in": select_status}})

def get_all_user_events_count(select_status):

    return len(find_distinct(current_app.config['EVENT_COLLECTION'], key="eventId",
                             condition={"sourceId": {"$exists": False},
                                        "eventStatus": {"$in": select_status}}))


def get_all_user_events_pagination(select_status, skip, limit):

    eventIds = find_distinct(current_app.config['EVENT_COLLECTION'], key="eventId",
                             condition={"sourceId": {"$exists": False},
                                        "eventStatus": {"$in": select_status}},
                             skip=skip,
                             limit=limit)
    begin = skip
    end = min(len(eventIds), skip+limit)
    events_by_eventId = {}
    for eventId in eventIds[begin:end]:
        events = list(find_all(current_app.config['EVENT_COLLECTION'],
                               filter={"eventId": eventId,
                                       "eventStatus": {"$in": select_status}}))
        if events:
            events_by_eventId[eventId] = events

    return events_by_eventId


# TODO get searched posts
def get_searched_user_events(searchDic, select_status):

    searchDic['sourceId'] = {"$exists": False}
    searchDic['eventStatus'] = {"$in": select_status}
    return list(find_all(current_app.config['EVENT_COLLECTION'], filter=searchDic))

def find_user_event(objectId):
    try:
        _id = ObjectId(objectId)
    except InvalidId:
        return {}
    return find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)})


def update_user_event(objectId, update, delete_field=None):
    try:
        _id = ObjectId(objectId)
    except InvalidId:
        return {}
    updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)},
                              update={
                                  "$set": update
                              })
    if delete_field:
        updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)},
                                  update={
                                      "$unset": delete_field
                                  })

    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
        print("Update {} fails in update_user_event".format(objectId))

def find_user_all_object_events(eventId):
    print(eventId)
    result_events =  find_all(current_app.config['EVENT_COLLECTION'], filter={"eventId": eventId})
    if result_events is None:
        return []
    return result_events


def create_new_user_event(new_user_event):
    update_result = None
    result = insert_one(current_app.config['EVENT_COLLECTION'], new_user_event)
    if result.inserted_id:
        update = dict()
        update['eventStatus'] = 'pending'
        update['eventId'] = result.inserted_id
        update_result = update_one(current_app.config['EVENT_COLLECTION'],
                                   condition={"_id": ObjectId(result.inserted_id)},
                                   update={
                                      "$set": update
                                  })
    if update_result is None or update_result.modified_count == 0 and update_result.matched_count == 0 and update_result.upserted_id is None:
        print("create_new_user_event {} failed")
    return result.inserted_id

def delete_user_event(eventId):
    pass

# Find the approval status for one event
def get_user_event_status(objectId):
    pass

def approve_user_event(objectId):
    pass

def disapprove_user_event(objectId):
    pass


def populate_event_from_form(post_form):
    new_event = dict()
    for item in post_form:
        new_event[item] = post_form.get(item)
    return new_event
