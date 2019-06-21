from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..db import find_all, find_one, update_one

def get_all_user_events(select_status):
    if not select_status:
        select_status = ['pending']
    return find_all(current_app.config['EVENT_COLLECTION'], filter={"sourceId": {"$exists": False},
                                                                    "eventStatus": {"$in": select_status}})

# TODO get searched posts
def get_searched_user_events(searchDic, select_status):
    if not select_status:
        select_status = ['pending']
    searchDic['sourceId'] = {"$exists": False}
    searchDic['eventStatus'] = {"$in": select_status}
    return find_all(current_app.config['EVENT_COLLECTION'], filter=searchDic)

def find_user_event(objectId):
    try:
        _id = ObjectId(objectId)
    except InvalidId:
        return {}
    return find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)})


def update_user_event(objectId, update):
    try:
        _id = ObjectId(objectId)
    except InvalidId:
        return {}
    updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)},
                              update={
                                  "$set": update
                              })

    if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
        print("Update {} fails in update_user_event".format(objectId))

def delete_user_event(eventId):
    pass

# Find the approval status for one event
def get_user_event_status(objectId):
    pass

def approve_user_event(objectId):
    pass

def disapprove_user_event(objectId):
    pass
