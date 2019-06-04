from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..db import find_all, find_one, update_one

def get_all_user_events():
    return find_all(current_app.config['EVENT_COLLECTION'], filter={"sourceId": {"$exists": False}})


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
    return update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)},
                      update={
                          "$set": update
                      })

 
def delete_user_event(eventId):
    pass
