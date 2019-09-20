import os
import json
import boto3
import datetime
import requests
import traceback

from PIL import Image
from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..db import find_all, find_one, update_one, update_many, find_one_and_update, get_count, insert_one
from .downloadImage import downloadImage
# find many events in a calendar with selected status
def get_calendar_events(sourceId, calendarId, select_status):

    print(select_status)
    return find_all(current_app.config['EVENT_COLLECTION'], filter={"sourceId": sourceId,
                                                                    "calendarId": calendarId,
                                                                    "eventStatus": {"$in": select_status} })

# find the count of events in a calendar with selected status
def get_calendar_events_count(sourceId, calendarId, select_status):

    return get_count(current_app.config['EVENT_COLLECTION'],
                     {"sourceId": sourceId ,
                      "calendarId": calendarId,
                     "eventStatus": {"$in": select_status}})

# find many events in a calendar with selected status with pagination
def get_calendar_events_pagination(sourceId, calendarId, select_status, skip, limit):

    events = find_all(current_app.config['EVENT_COLLECTION'],
                        filter={
                        "sourceId": sourceId,
                        "calendarId": calendarId,
                        "eventStatus": {"$in": select_status}
                        }, skip=skip, limit=limit)
    return events


# Approve events from a calendar
def approve_calendar_events(calendarId):
    updateResult = update_many(current_app.config['EVENT_COLLECTION'], condition={"calendarId": calendarId}, update={
        "$set": {"eventStatus": "approved"}
    })

# Disapprove events from a calendar
def disapprove_calendar_events(calendarId):
    updateResult = update_many(current_app.config['EVENT_COLLECTION'], condition={"calendarId": calendarId}, update={
        "$set": {"eventStatus": "disapproved"}
    })


def publish_event(id, imageId):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + current_app.config['AUTHENTICATION_TOKEN']
    }
    try:
        platform_event_id = None
        event = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)},
                         projection={'_id': 0, 'eventStatus': 0})

        if event:
            print("event {} submit method: {}".format(id, event['submitType']))
            if event.get('startDate'):
                if isinstance(event.get('startDate'), datetime.date):
                    event['startDate'] = event['startDate'].isoformat()
                event['startDate'] = datetime.datetime.strptime(event['startDate'], "%Y-%m-%dT%H:%M:%S")
                event['startDate'] = event['startDate'].strftime("%Y/%m/%dT%H:%M:%S")
            if event.get('endDate'):
                if isinstance(event.get('endDate'), datetime.date):
                    event['endDate'] = event['endDate'].isoformat()
                event['endDate'] = datetime.datetime.strptime(event['endDate'], "%Y-%m-%dT%H:%M:%S")
                event['endDate'] = event['endDate'].strftime("%Y/%m/%dT%H:%M:%S")

            if imageId:
                event['imageURL'] = current_app.config['ROKWIRE_IMAGE_LINK_FORMAT'].format(id, imageId)

            submit_type = event['submitType']
            del event['submitType']

            if submit_type == 'post':
                result = requests.post(current_app.config['EVENT_BUILDING_BLOCK_URL'], headers=headers,
                                       data=json.dumps(event))
                # Get platform event ID and store in the Events Manager database.
                platform_event_id = result.json()['id']
            elif submit_type == 'put':
                url = current_app.config['EVENT_BUILDING_BLOCK_URL'] + '/' + event.get('platformEventId')
                # Remove platform event ID from request
                if "platformEventId" in event:
                    del event["platformEventId"]
                result = requests.put(url, headers=headers,
                                      data=json.dumps(event))
            elif submit_type == 'patch':
                url = current_app.config['EVENT_BUILDING_BLOCK_URL'] + '/' + event.get('platformEventId')
                # Remove platform event ID from request
                if "platformEventId" in event:
                    del event["platformEventId"]
                result = requests.patch(url, headers=headers,
                                        data=json.dumps(event))

            if result.status_code not in (200, 201):
                print("Event {} submission fails".format(id))
                return False
            else:
                if submit_type == 'post':
                    updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)}, update={
                        "$set": {"eventStatus": "published", 'platformEventId': platform_event_id}
                    })
                else:
                    updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)},
                                              update={
                                                  "$set": {"eventStatus": "published"}
                                              })
                if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                    print("Publish event {} fails in publish_event".format(id))

                return True


    except Exception:
        traceback.print_exc()
        return False


def publish_image(id):
    headers = {
        'Content-Type': 'image/png', 
        'Authorization': 'Bearer ' + current_app.config['AUTHENTICATION_TOKEN']
    }
    try:

        record = find_one(current_app.config['IMAGE_COLLECTION'], condition={"eventId": id})

        submit_type = 'post'
        image = open('{}/{}.png'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id), 'rb')
        url = "{}/{}".format(current_app.config['ROKWIRE_IMAGE_LINK_PREFIX'], id)

        # if there is record shows image has been submit before then change post to put
        if record:
            if record.get('submitBefore'):
                submit_type = 'put'

        if submit_type == 'post':
            response = requests.post(url, data=image.read(), headers=headers)
        elif submit_type == 'put':
            response = requests.put(url, data=image.read(), headers=headers)

        image.close()


        if response.status_code in (200, 201):
            updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                                      condition={'eventId': id},
                                      update={"$set": { 'submitBefore': True,
                                                        'eventId': id}}, upsert=True)
            if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                print("Update {} fails in update_user_event".format(id))

            return True

        else:
            updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                            condition={'eventId': id},
                            update={"$set": { 'submitBefore': False,
                                              'eventId': id}}, upsert=True)
            if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                print("Update {} fails in update_user_event".format(id))

            return False

    except Exception:
        traceback.print_exc()
        return False

    finally:
        if os.path.exists('{}/{}.png'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id)):
            os.remove('{}/{}.png'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id))

    return True

def s3_publish_image(id, client):

    try:

        record = find_one(current_app.config['IMAGE_COLLECTION'], condition={"eventId": id})
        image_png_location = '{}/{}.png'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id)

        # convert from png to jpg and save it
        with Image.open(image_png_location) as im:
            im.convert('RGB').save('{}/{}.jpg'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id),
                                    quality=95)


        # if there is no record before, insert it to get the id
        if not record:
            insertResult = insert_one(current_app.config['IMAGE_COLLECTION'], document={
                'eventId': id
            })
            if insertResult.inserted_id:
                imageId = str(insertResult.inserted_id)
            else:
                return None
        else:
            imageId = str(record['_id'])


        client.upload_file(
            '{}/{}.jpg'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id),
            current_app.config['BUCKET'],
            '{}/{}/{}.jpg'.format(current_app.config['AWS_IMAGE_FOLDER_PREFIX'], id, imageId)
        )

    except Exception:
        traceback.print_exc()
        print("Upload image for event {} failed".format(id))
        return None

    finally:
        if os.path.exists('{}/{}.png'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id)):
            os.remove('{}/{}.png'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id))

        if os.path.exists('{}/{}.jpg'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id)):
            os.remove('{}/{}.jpg'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id))

    return imageId

def approve_event(id):
    print("{} is going to be approved".format(id))
    result = find_one_and_update(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)}, update={
        "$set": {"eventStatus":  "approved"}
    })
    if not result:
        print("Approve event {} fails in approve_event".format(id))

    download_image_result = downloadImage(
        result['calendarId'],
        result['dataSourceEventId'],
        id
    )

    upload_image_result = False
    if download_image_result:
        upload_image_result = publish_image(id)
    publish_event(id, upload_image_result)

# disapprove a calendar event
def disapprove_event(id):
    print("{} is going to be disapproved".format(id))
    result = find_one_and_update(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)}, update={
        "$set": {"eventStatus":  "disapproved"}
    })
    if not result:
        print("Disapprove event {} fails in disapprove_event".format(id))


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
    approve_calendar_events(calendarId)

# Disapprove a calendar and relevant events
def disapprove_calendar_db(calendarId):
    updateResult = update_one(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId},
                              update={
                                  "$set": {"status": "disapproved"}
                              }, upsert=True)
    disapprove_calendar_events(calendarId)

# Find the approval status for one calendar
def get_calendar_status(calendarId):
    calendar = find_one(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId})
    if not calendar:
        return None
    return calendar['status']

# Find the approval status for many calendars
def get_all_calendar_status():
    calendars = find_all(current_app.config['CALENDAR_COLLECTION'], filter={})
    result = {}
    for dict in current_app.config['INT2CAL']:
        for calendarId, name in dict.items():
            calendar = find_one(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId})
            # print(calendar)
            if calendar:
                result[calendarId] = calendar["status"]
            else:
                result[calendarId] = None
    return result

# Update approval status for many calendars (and relevant events)
def update_calendars_status(update, allstatus):
    for calendarId in allstatus.keys():
        if calendarId in update: # approve
            approve_calendar_db(calendarId)
        else: # disapprove
            disapprove_calendar_db(calendarId)

# Get search events count
def get_search_events_count(conditions, select_status):
    if not conditions:
        return 0
    else:
        conditions['eventStatus'] = {"$in": select_status}
        return get_count(current_app.config['EVENT_COLLECTION'],
                         conditions)


# Search for events satisfying conditions
def get_search_events(conditions, select_status, skip, limit):
    if not conditions:
        return []
    else:
        conditions['eventStatus'] = {"$in": select_status}
        conditions['sourceId'] = {"$exists": True}
        return find_all(current_app.config['EVENT_COLLECTION'],
                        filter=conditions, skip=skip, limit=limit)
