import requests
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
def publish_event(id):
    try:
        event = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)}, 
                        projection={'_id': 0, 'eventStatus':0})
        print("event {} submit method: {}".format(id, event['submitType']))
        if event['submitType'] == 'post':
            result = requests.post(current_app.config['EVENT_BUILDING_BLOCK_URL'], data=event)
        elif event['submitType'] == 'put':
            result = requests.put(current_app.config['EVENT_BUILDING_BLOCK_URL'], data=event)
        elif event['submitType'] == 'patch':
            result = requests.patch(current_app.config['EVENT_BUILDING_BLOCK_URL'], data=event)
        
        if result.status_code != 200:
            print("Submission fails")
        

    except Exception as e :
        print(e)


def approve_event(id):
    print("{} is going to be approved".format(id))
    update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)}, update={
        "$set": {"eventStatus":  "approved"}
    })
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
        print("Update {} fails".format(objectId))


def approve_calendar_db(calendarId):
    pass