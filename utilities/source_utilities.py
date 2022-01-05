#  Copyright 2020 Board of Trustees of the University of Illinois.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import os.path
from os import path
import json
import boto3
import datetime
import requests
import traceback

from PIL import Image
from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..db import find_all, find_one, update_one, update_many, find_one_and_update, get_count, insert_one, delete_events_in_list
from .downloadImage import downloadImage

from ..config import Config

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


def publish_event(id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + current_app.config['AUTHENTICATION_TOKEN']
    }
    platform_event_id = None
    try:
        event = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)},
                         projection={'_id': 0, 'eventStatus': 0})
        platform_event_id = event.get('platformEventId')
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
                return False, None
            else:
                imageId = publish_image(id, platform_event_id)
                if submit_type == 'post':
                    if imageId:
                        updates = {"eventStatus": "published", 'platformEventId': platform_event_id, "imageURL": current_app.config['ROKWIRE_IMAGE_LINK_FORMAT'].format(platform_event_id, imageId)}
                    else:
                        updates = {"eventStatus": "published", 'platformEventId': platform_event_id}
                    updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)}, update={
                        "$set": updates
                    })
                else:
                    if imageId:
                        updates = {"eventStatus": "published", "imageURL": current_app.config['ROKWIRE_IMAGE_LINK_FORMAT'].format(platform_event_id, imageId)}
                    else:
                        updates = {"eventStatus": "published"}
                    updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)},
                                              update={
                                                  "$set": updates
                                              })
                if imageId:
                    event['imageURL'] = current_app.config['ROKWIRE_IMAGE_LINK_FORMAT'].format(platform_event_id, imageId)
                    url = current_app.config['EVENT_BUILDING_BLOCK_URL'] + '/' + platform_event_id
                    # Remove platform event ID from request
                    if "platformEventId" in event:
                        del event["platformEventId"]
                    result = requests.put(url, headers=headers,
                                          data=json.dumps(event))
                    if result.status_code not in (200, 201):
                        print("Event {} submission fails".format(id))
                        return False, None

                if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                    print("Publish event {} fails in publish_event".format(id))

                return True, imageId


    except Exception:
        traceback.print_exc()
        return False, None


def publish_image(id, platformId):
    imageId = None
    headers = {
        'Authorization': 'Bearer ' + current_app.config['AUTHENTICATION_TOKEN']
    }
    try:
        record = find_one(current_app.config['IMAGE_COLLECTION'], condition={"eventId": id})

        submit_type = 'post'
        image = None
        imagePath = '{}/{}.jpg'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id)
        if path.exists(imagePath):
            image = open(imagePath, 'rb')
        else:
            return None
        url = "{}/{}/images".format(current_app.config['EVENT_BUILDING_BLOCK_URL'], platformId)

        # if there is record shows image has been submit before then change post to put
        if record:
            if record.get('submitBefore'):
                submit_type = 'put'
        file = {'file': image}
        if submit_type == 'post':
            response = requests.post(url, files=file, headers=headers)
        elif submit_type == 'put':
            response = requests.put(url, files=file, headers=headers)
        image.close()


        if response.status_code in (200, 201):
            imageId = response.json()['id']
            updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                                      condition={'eventId': id},
                                      update={"$set": { 'submitBefore': True,
                                                        'eventId': id}}, upsert=True)
            if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                print("Update {} fails in update_user_event".format(id))
        else:
            updateResult = update_one(current_app.config['IMAGE_COLLECTION'],
                            condition={'eventId': id},
                            update={"$set": { 'submitBefore': False,
                                              'eventId': id}}, upsert=True)
            if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                print("Update {} fails in update_user_event".format(id))
    except Exception:
        traceback.print_exc()

    finally:
        if os.path.exists('{}/{}.png'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id)):
            os.remove('{}/{}.png'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id))
        if os.path.exists('{}/{}.jpg'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id)):
            os.remove('{}/{}.jpg'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id))
    return imageId

def s3_publish_image(id, client):
    image_location = ''
    try:
        record = find_one(current_app.config['IMAGE_COLLECTION'], condition={"eventId": id})
        for extension in Config.ALLOWED_IMAGE_EXTENSIONS:
            if os.path.isfile('{}/{}.{}'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id, extension)):
                image_location = '{}/{}.{}'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], id, extension)
                break
        if image_location == '':
            raise FileNotFoundError("Image for event {} not found".format(id))
        # convert to jpg and save it
        with Image.open(image_location) as im:
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
            '{}/{}/{}.jpg'.format(current_app.config['AWS_IMAGE_FOLDER_PREFIX'], id, imageId),
            ExtraArgs={
                'ACL': 'bucket-owner-full-control'
            }
        )

    except Exception:
        traceback.print_exc()
        print("Upload image for event {} failed".format(id))
        return None

    finally:
        if os.path.exists(image_location):
            os.remove(image_location)

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

    downloadImage(
        result['originatingCalendarId'],
        result['dataSourceEventId'],
        id
    )
    publish_event(id)

# disapprove a calendar event
def disapprove_event(id):
    print("{} is going to be disapproved".format(id))
    result = find_one_and_update(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)}, update={
        "$set": {"eventStatus":  "approved"}
    })
    if not result:
        print("Disapprove event {} fails in disapprove_event".format(id))
    else:
        if result.get("platformEventId"):
            objectId_list_to_delete = list()
            objectId_list_to_delete.append(ObjectId(id))
            delete_events_in_building_block(objectId_list_to_delete)
            find_one_and_update(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(id)}, update={
                "$set": {"submitType": "post", "platformEventId": None}})


def get_event(objectId):
    # temporary solution for online event location display
    event = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)})
    filter_online_location(event)
    return event

def get_download_schedule_time():
    schedule_time = find_one('schedule_time', condition={ "time": { '$exists': True }})
    return schedule_time.get('time')

def update_download_schedule_time(schedule_time):
    update_time = {"time": schedule_time}
    update_one('schedule_time', condition={ "time": { '$exists': True }}, update={
                                  "$set": update_time
                              })

def init_download_schedule_time(schedule_time):
    insert_one('schedule_time', document={"time": schedule_time})

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
    for calendar in calendars:
        result[calendar.get('calendarId')] = calendar
    return result


def load_calendar_into_db():
    for calendar in current_app.config['INT2CAL']:
        for calendarId, calendarName in calendar.items():
            doc = find_one(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId})
            if not doc:
                insert_one(current_app.config['CALENDAR_COLLECTION'], document={"calendarId": calendarId, "calendarName": calendarName,
                                                                                "status": "disapproved"})
            elif not doc.get('calendarName'):
                find_one_and_update(current_app.config['CALENDAR_COLLECTION'], condition={"calendarId": calendarId},
                                    update={"$set": {"calendarName": calendarName}})

    print("load calendar into db")


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
        events = find_all(current_app.config['EVENT_COLLECTION'],
                        filter=conditions, skip=skip, limit=limit)
        
        # temporary solution for online event location display
        for event in events:
            filter_online_location(event)
        return events


# delete events in building block
def delete_events_in_building_block(objectId_list_to_delete):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + current_app.config['AUTHENTICATION_TOKEN']
    }
    delete_success_list = []
    fail_count = 0
    for _id in objectId_list_to_delete:
        event = find_one(current_app.config['EVENT_COLLECTION'], condition= _id)
        url = current_app.config['EVENT_BUILDING_BLOCK_URL'] + '/' + str(event.get('platformEventId'))
        result = requests.delete(url, headers=headers)
        if result.status_code != 202 and result.status_code != 404:
            print("Event {} deletion fails".format(_id))
            fail_count +=1
        else:
            delete_success_list.append(_id)
    success_count = len(delete_success_list)

    print("failed deleted in building block: " + str(fail_count))
    print("successful deleted in building block: " + str(success_count))
    return delete_success_list

def delete_events(objectId_list_to_delete):
    delete_events_remote = delete_events_in_building_block(objectId_list_to_delete)
    delete_events_local = delete_events_in_list(current_app.config['EVENT_COLLECTION'], delete_events_remote)
    return delete_events_local


def filter_online_location(event):
    if event:
        location_description = event.get("location", {}).get("description", "")
        if location_description == "":
            return event
        else:
            for excluded_location in Config.EXCLUDED_LOCATION:
                if excluded_location.lower() in location_description.lower():
                    event["location"]["latitude"] = None
                    event["location"]["longitude"] = None
                    return event
    return event

# Find the approval status for one event
def event_status(objectId):
    event = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)})
    event_status = event['eventStatus']
    return event_status
