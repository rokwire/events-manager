from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..db import find_all, find_one, update_one, find_distinct, insert_one, find_one_and_update, delete_events_in_list

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

def delete_user_event(eventId):
    id = ObjectId(eventId)
    delete_list = []
    delete_list.append(id)
    successfull_delete_list = delete_events_in_list(current_app.config['EVENT_COLLECTION'], delete_list)
    return id


# Find the approval status for one event
def get_user_event_status(objectId):
    pass

def approve_user_event(objectId):
    print("{} is going to be approved".format(id))
    result = find_one_and_update(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)}, update={
        "$set": {"eventStatus":  "approved"}
    })
    if not result:
        print("Approve event {} fails in approve_event".format(id))


def disapprove_user_event(objectId):
    print("{} is going to be disapproved".format(id))
    result = find_one_and_update(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)}, update={
        "$set": {"eventStatus":  "pending"}
    })
    if not result:
        print("Disapprove event {} fails in disapprove_event".format(id))
