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

import pytz
import json
import datetime
import requests
import traceback
import googlemaps
import os
import re
import tempfile
import shutil
from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from dateutil import tz
from .source_utilities import s3_publish_image
from PIL import Image
import boto3
import os
import glob
from ..config import Config
from .constants import *
from .event_time_conversion import *
from ..db import find_all, find_one, update_one, find_distinct, insert_one, find_one_and_update, delete_events_in_list, \
    text_index_search

GOOGLEKEY = Config.GOOGLE_KEY
gmaps = googlemaps.Client(key=GOOGLEKEY)

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
    end = min(len(eventIds), skip + limit)
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
    result_events = find_all(current_app.config['EVENT_COLLECTION'], filter={"eventId": eventId})
    if result_events is None:
        return []
    return result_events


def delete_user_event_in_building_block(objectId_list):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + current_app.config['AUTHENTICATION_TOKEN']
    }
    delete_success_list = []
    fail_count = 0
    for _id in objectId_list:
        event = find_one(current_app.config['EVENT_COLLECTION'], condition=_id)
        url = current_app.config['EVENT_BUILDING_BLOCK_URL'] + '/' + str(event.get('platformEventId'))
        try:
            result = requests.delete(url, headers=headers)
            if result.status_code != 202:
                print("Event {} deletion fails".format(_id))
                fail_count += 1
            else:
                delete_success_list.append(_id)
        except requests.exceptions.RequestException as err:
            print("Unexpected network error when deleting user event {}:".format(_id), err)
            fail_count += 1
    success_count = len(delete_success_list)

    print("failed deleted in building block: " + str(fail_count))
    print("successfully deleted in building block: " + str(success_count))
    return delete_success_list


def delete_user_event(eventId):
    # Fetching event status
    event_status = get_user_event_status(eventId)

    # Deleting 'pending' events off of the local db
    if event_status == 'pending':
        local_del_id = ObjectId(eventId)
        local_delete_list = []
        local_delete_list.append(local_del_id)
        local_delete_event_local = delete_events_in_list(current_app.config['EVENT_COLLECTION'], local_delete_list)
        local_delete_count = len(local_delete_event_local)
        if local_delete_count < 1:
            print("Local event {} deletion failed".format(eventId))
            return
        else:
            print("Local event {} deletion successful".format(eventId))
            return local_delete_event_local[0]

    # Deleting 'published' events off of the building block and then the local db
    elif event_status == 'approved':
        id = ObjectId(eventId)
        delete_list = []
        delete_list.append(id)
        successfull_delete_list = delete_user_event_in_building_block(delete_list)
        delete_count = len(successfull_delete_list)
        # Since we're only dealing with deleting a singular item at a time
        # if delete_count < 1, the item wasn't successfully deleted off of the events building block
        if delete_count < 1:
            print("Local and remote event {} deletion failed".format(eventId))
            return
        else:
            delete_event_local = delete_events_in_list(current_app.config['EVENT_COLLECTION'], successfull_delete_list)
            print("Local and remote event {} deletion successful".format(eventId))
            return delete_event_local[0]


# Find the approval status for one event
def get_user_event_status(objectId):
    event = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)})
    event_status = event['eventStatus']
    return event_status


def approve_user_event(objectId):
    print("{} is going to be approved".format(objectId))
    result = find_one_and_update(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)}, update={
        "$set": {"eventStatus": "approved"}
    })
    if not result:
        print("Approve event {} fails in approve_event".format(id))


def publish_user_event(eventId):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + current_app.config['AUTHENTICATION_TOKEN']
    }

    try:
        # Put event in object, but exclude ID and status
        event = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(eventId)},
                         projection={'_id': 0, 'eventStatus': 0})

        # Should upload user images
        s3_client = boto3.client('s3')
        imageId = s3_publish_image(eventId, s3_client)
        if imageId:
            print("User image upload successful for event {}".format(eventId))
            event['imageURL'] = current_app.config['ROKWIRE_IMAGE_LINK_FORMAT'].format(eventId, imageId)

        if event:
            # Formatting Date and time for json dump
            if event.get('startDate'):
                if isinstance(event.get('startDate'), str):
                    event['startDate'] = datetime.strptime(event.get('startDate'), '%Y-%m-%dT%H:%M:%S')
                elif isinstance(event.get('startDate'), datetime.date):
                    event['startDate'] = event['startDate'].isoformat()
                    event['startDate'] = datetime.datetime.strptime(event['startDate'], "%Y-%m-%dT%H:%M:%S")
                event['startDate'] = event['startDate'].strftime("%Y/%m/%dT%H:%M:%S")
            if event.get('endDate'):
                if isinstance(event.get('endDate'), str):
                    event['endDate'] = datetime.strptime(event.get('endDate'), '%Y-%m-%dT%H:%M:%S')
                elif isinstance(event.get('endDate'), datetime.date):
                    event['endDate'] = event['endDate'].isoformat()
                    event['endDate'] = datetime.datetime.strptime(event['endDate'], "%Y-%m-%dT%H:%M:%S")
                event['endDate'] = event['endDate'].strftime("%Y/%m/%dT%H:%M:%S")
            if event.get('eventId'):
                del event['eventId']

            # event = {k: v for k, v in event.items() if v}
            if 'subcategory' in event.keys() and event['subcategory'] is None:
                event['subcategory'] = ''
            if 'targetAudience' in event.keys() and event['targetAudience'] is None:
                event['targetAudience'] = []
            if 'contacts' in event.keys() and event['contacts'] is None:
                event['contacts'] = []
            if 'tags' in event.keys() and event['tags'] is None:
                event['tags'] = []
            if 'subEvents' in event.keys() and event['subEvents'] is None:
                event['subEvents'] = []
            if 'location' in event.keys() and event['location'] is None:
                event['location'] = dict()
            # Setting up post request
            result = requests.post(current_app.config['EVENT_BUILDING_BLOCK_URL'], headers=headers,
                                   data=json.dumps(event))

            # if event submission fails, print that out and change status back to pending
            if result.status_code != 201:
                print("Event {} submission fails".format(eventId))
                failed_event = find_one_and_update(current_app.config['EVENT_COLLECTION'],
                                                   condition={"_id": ObjectId(eventId)}, update={
                        "$set": {"eventStatus": "pending"}
                    })
                return False
            # if successful, change status of event to approved.
            else:
                platform_event_id = result.json()['id']
                updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(eventId)},
                                          update={
                                              "$set": {"eventStatus": "approved", "platformEventId": platform_event_id}
                                          })
                return True

    except Exception:
        traceback.print_exc()
        return False


def put_user_event(eventId):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + current_app.config['AUTHENTICATION_TOKEN']
    }
    try:
        # Put event in object, but exclude ID and status
        event = find_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(eventId)},
                         projection={'_id': 0, 'eventStatus': 0})
        if event:
            # Formatting Date and time for json dump
            if event.get('startDate'):
                if isinstance(event.get('startDate'), str):
                    event['startDate'] = datetime.strptime(event.get('startDate'), '%Y-%m-%dT%H:%M:%S')
                elif isinstance(event.get('startDate'), datetime.date):
                    event['startDate'] = event['startDate'].isoformat()
                    event['startDate'] = datetime.datetime.strptime(event['startDate'], "%Y-%m-%dT%H:%M:%S")
                event['startDate'] = event['startDate'].strftime("%Y/%m/%dT%H:%M:%S")
            if event.get('endDate'):
                if isinstance(event.get('endDate'), str):
                    event['endDate'] = datetime.strptime(event.get('endDate'), '%Y-%m-%dT%H:%M:%S')
                elif isinstance(event.get('endDate'), datetime.date):
                    event['endDate'] = event['endDate'].isoformat()
                    event['endDate'] = datetime.datetime.strptime(event['endDate'], "%Y-%m-%dT%H:%M:%S")
                event['endDate'] = event['endDate'].strftime("%Y/%m/%dT%H:%M:%S")
            if event.get('eventId'):
                del event['eventId']

            # Getting rid of all the empty fields for PUT request
            # event = {k: v for k, v in event.items() if v}
            if 'subcategory' in event.keys() and event['subcategory'] is None:
                event['subcategory'] = ''
            if 'targetAudience' in event.keys() and event['targetAudience'] is None:
                event['targetAudience'] = []
            if 'contacts' in event.keys() and event['contacts'] is None:
                event['contacts'] = []
            if 'tags' in event.keys() and event['tags'] is None:
                event['tags'] = []
            if 'subEvents' in event.keys() and event['subEvents'] is None:
                event['subEvents'] = []
            if 'location' in event.keys() and event['location'] is None:
                event['location'] = dict()
            # Generation of URL via platformEventId
            url = current_app.config['EVENT_BUILDING_BLOCK_URL'] + '/' + event.get('platformEventId')
            # Getting rid of platformEventId from PUT request
            if "platformEventId" in event:
                del event["platformEventId"]

            # PUT request
            result = requests.put(url, headers=headers, data=json.dumps(event))

            # If PUT request fails, print that out and change status back to pending
            if result.status_code != 200:
                print("Event {} submission fails".format(eventId))
                failed_event = find_one_and_update(current_app.config['EVENT_COLLECTION'],
                                                   condition={"_id": ObjectId(eventId)}, update={
                        "$set": {"eventStatus": "pending"}
                    })
                return False

            # If PUT request successful, change status to approved
            else:
                updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(eventId)},
                                          update={
                                              "$set": {"eventStatus": "approved"}
                                          })
                return True

    except Exception:
        traceback.print_exc()
        return False


def disapprove_user_event(objectId):
    print("{} is going to be disapproved".format(objectId))
    result = find_one_and_update(current_app.config['EVENT_COLLECTION'], condition={"_id": ObjectId(objectId)}, update={
        "$set": {"eventStatus": "pending"}
    })
    if not result:
        print("Disapprove event {} fails in disapprove_event".format(objectId))


def create_new_user_event(new_user_event):
    update_result = None
    result = insert_one(current_app.config['EVENT_COLLECTION'], new_user_event)
    if result.inserted_id:
        update = dict()
        update['eventStatus'] = 'pending'
        update['eventId'] = str(result.inserted_id)
        # for key in update:
        update_result = update_one(current_app.config['EVENT_COLLECTION'],
                                   condition={"_id": ObjectId(result.inserted_id)},
                                   update={
                                       "$set": update
                                   })
    if update_result is None or update_result.modified_count == 0 and update_result.matched_count == 0 and update_result.upserted_id is None:
        print("create_new_user_event {} failed")
    return result.inserted_id


def populate_event_from_form(post_form, email):
    new_event = dict()
    super_event = False
    all_day_event = False
    for item in post_form:
        if item_not_list(item):
            if item == 'isSuperEvent' and post_form.get(item) == 'on':
                new_event['isSuperEvent'] = True
                super_event = True
            elif item == 'allDay' and post_form.get(item) == 'on':
                new_event['allDay'] = True
                all_day_event = True
            elif item == 'isVirtual' and post_form.get(item) == 'on':
                new_event['isVirtual'] = True
            else:
                new_event[item] = post_form.get(item)
    if not super_event:
        new_event['isSuperEvent'] = False
    if not all_day_event:
        new_event['allDay'] = False

    new_event['contacts'] = get_contact_list(post_form)

    if new_event['isSuperEvent'] == True:
        new_event['subEvents'] = get_subevent_list(post_form)
    else:
        new_event['subEvents'] = None

    new_event['tags'] = get_tags(post_form)

    new_event['targetAudience'] = get_target_audience(post_form)

    start_date = post_form.get('startDate')

    new_event['startDate'] = get_datetime_in_utc(post_form.get('location'), start_date, 'startDate', all_day_event)

    end_date = post_form.get('endDate')
    if end_date != '':
        new_event['endDate'] = get_datetime_in_utc(post_form.get('location'), end_date, 'endDate', all_day_event)

    location = post_form.get('location')
    if location != '':
        new_event['location'] = get_location_details(location)
    else:
        new_event['location'] = None

    new_event['createdBy'] = email

    return new_event


def get_location_details(location_description):
    location_obj = dict()
    for excluded_location in Config.EXCLUDED_LOCATION:
        if excluded_location.lower() in location_description.lower():
            location_obj['description'] = location_description
            return location_obj
    google_geocoding_api_key = current_app.config['GOOGLE_KEY']
    try:
        google_maps_client = googlemaps.Client(key=google_geocoding_api_key)
        geocoding_response = google_maps_client.geocode(address=location_description + ',Urbana',
                                                        components={'administrative_area': 'Urbana', 'country': "US"})
        if len(geocoding_response) > 0:
            lat = geocoding_response[0]['geometry']['location']['lat']
            lng = geocoding_response[0]['geometry']['location']['lng']
            location_obj = {
                'latitude': lat,
                'longitude': lng,
                'description': location_description
            }
        else:
            location_obj['description'] = location_description
    except ValueError as e:
        print("Error in connecting to Google Geocoding API: {}".format(e))
        location_obj['description'] = location_description
    except googlemaps.exceptions.ApiError as e:
        print("API Key Error: {}".format(e))
        location_obj['description'] = location_description

    return location_obj


def get_datetime_in_utc(location, str_local_date, date_field, is_all_day_event):
    print("str_local_date", str_local_date)
    if is_all_day_event:
        datetime_obj = datetime.strptime(str_local_date, "%Y-%m-%d")
        # Set time to match the
        if date_field == "startDate":
            datetime_obj = datetime_obj.replace(hour=00, minute=00)
        elif date_field == "endDate":
            datetime_obj = datetime_obj.replace(hour=23, minute=59)
    else:
        try:
            datetime_obj = datetime.strptime(str_local_date, "%Y-%m-%dT%H:%M")
        except ValueError:
            datetime_obj = datetime.strptime(str_local_date, "%Y-%m-%dT%H:%M:%S")
    if location:
        latitude = None
        longitude = None
        if location in predefined_locations:
            latitude = predefined_locations[location].latitude
            longitude = predefined_locations[location].longitude
        else:
            try:
                GeoResponse = gmaps.geocode(address=location + ',Urbana',
                                            components={'administrative_area': 'Urbana', 'country': "US"})
                if len(GeoResponse) != 0:
                    latitude = GeoResponse[0]['geometry']['location']['lat']
                    longitude = GeoResponse[0]['geometry']['location']['lng']
            except googlemaps.exceptions.ApiError as e:
                print("API Key Error: {}".format(e))
        return utctime(datetime_obj, latitude, longitude)
    local_tz = pytz.timezone("US/Central")
    datetime_with_tz = local_tz.localize(datetime_obj, is_dst=None)  # No daylight saving time
    datetime_obj = datetime_with_tz.astimezone(pytz.UTC)
    return datetime_obj.strftime("%Y-%m-%dT%H:%M:%S")


def get_datetime_in_local(location, str_utc_date, is_all_day_event):
    timezone = pytz.UTC
    localzone = tz.tzlocal()
    if location and location.get('latitude') and location.get('longitude'):
        latitude = location.get('latitude')
        longitude = location.get('longitude')
        timezone_str = get_timezone_by_geolocation(latitude, longitude)
        localzone = tz.gettz(timezone_str)

    datetime_obj = datetime.strptime(str_utc_date[0:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone).astimezone(localzone)

    if is_all_day_event:
        return datetime_obj.strftime("%Y-%m-%d")
    else:
        return datetime_obj.strftime("%Y-%m-%dT%H:%M:%S")


def get_contact_list(post_form):
    contacts_arrays = []
    has_contacts_in_request = False
    for item in post_form:
        # when contact input field is not empty
        if item == 'firstName' or item == 'lastName' or item == 'email' or item == 'phone' or item == 'organization':
            contact_list = post_form.getlist(item)
            if len(contact_list) != 0:
                # delete first group of empty string
                contact_list = contact_list[1:]
                contacts_arrays += [contact_list]
        # new_event[item] = post_form.get(item)

    if contacts_arrays:
        num_of_contacts = len(contacts_arrays[0])
        contacts_dic = []
        for i in range(num_of_contacts):
            a_contact = {}
            firstName = contacts_arrays[0][i]
            lastName = contacts_arrays[1][i]
            email = contacts_arrays[2][i]
            phone = contacts_arrays[3][i]
            orginazation = contacts_arrays[4][i]
            if firstName != "":
                a_contact['firstName'] = firstName
            if lastName != "":
                a_contact['lastName'] = lastName
            if email != "":
                a_contact['email'] = email
            if phone != "":
                a_contact['phone'] = phone
            if orginazation != "":
                a_contact['organization'] = orginazation
            if a_contact != {}:
                contacts_dic.append(a_contact)
        if contacts_dic != []:
            has_contacts_in_request = True
            return contacts_dic
        # return ""


# helper function to get subevent
def get_subevent_list(post_form):
    subevent_arrays = []
    for item in post_form:
        if item == 'name' or item == 'id' or item == 'track' or item == 'isFeatured':
            sub_list = post_form.getlist(item)
            if len(sub_list) != 0:
                sub_list = sub_list[1:]
                subevent_arrays += [sub_list]
    if subevent_arrays:
        num_of_sub = len(subevent_arrays[0])
        subevent_dict = []
        for i in range(num_of_sub):
            a_subevent = {}
            sub_name = subevent_arrays[0][i]
            sub_id = subevent_arrays[1][i]
            sub_track = subevent_arrays[2][i]
            sub_feature = subevent_arrays[3][i]
            if sub_name != "":
                a_subevent['name'] = sub_name
            if sub_id != "":
                a_subevent['id'] = sub_id
            if sub_track != "":
                a_subevent['track'] = sub_track
            if sub_feature != "":
                if sub_feature == 'Featured':
                    a_subevent['isFeatured'] = True
                else:
                    a_subevent['isFeatured'] = False
            if a_subevent != {}:
                subevent_dict.append(a_subevent)
        if subevent_dict != []:
            return subevent_dict
        else:
            return None
    else:
        return None


def get_tags(post_form):
    tag_arrays = []
    for item in post_form:
        if item == 'tags':
            tag_arrays = post_form.getlist(item)
    if tag_arrays:
        num_of_tag = len(tag_arrays)
        tag_dict = []
        for i in range(num_of_tag):
            a_tag = {}
            tag_name = tag_arrays[i]
            if tag_name != "":
                a_tag = tag_name
            if a_tag != {}:
                tag_dict.append(a_tag)
        if tag_dict != []:
            return tag_dict


def get_target_audience(post_form):
    target_audience_arrays = []
    for item in post_form:
        if item == 'targetAudience':
            target_audience_arrays = post_form.getlist(item)
    if target_audience_arrays:
        num_of_target_audience = len(target_audience_arrays)
        target_audience_dict = []
        for i in range(num_of_target_audience):
            a_target_audience = {}
            target_audience_group = target_audience_arrays[i]
            if target_audience_group != "":
                a_target_audience = target_audience_group
            if a_target_audience != {}:
                target_audience_dict.append(a_target_audience)
        if target_audience_dict != []:
            return target_audience_dict


def item_not_list(item):
    if item not in ['firstName', 'lastName', 'email', 'phone', 'organization', "id", 'track', 'isFeatured', 'tags',
                    'targetAudience', 'startDate', 'endDate', 'location']:
        return True
    else:
        return False


# Uses the implemented text index search to search the queries and modify the search results to JSON
def beta_search(search_string):
    queries_returned = text_index_search(current_app.config['EVENT_COLLECTION'], search_string)
    list_queries = list(queries_returned)
    for query in list_queries:
        query['label'] = query.pop('title')
        query['value'] = query.pop('platformEventId')
    return list_queries


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_IMAGE_EXTENSIONS


def clickable_utility(platformEventId):
    try:
        record = find_one(current_app.config['EVENT_COLLECTION'], condition={"platformEventId": platformEventId})
        if record:
            return record['eventId']
        else:
            print("Record with platformEventId:{} does not exist".format(platformEventId))

    except Exception:
        traceback.print_exc()
        print("Record with platformEventId:{} does not exist".format(platformEventId))
        return False


# S3 Utilities

# Initialization of global client
client = boto3.client('s3')

def s3_image_delete(eventId, imageId):
    try:
        record = find_one(current_app.config['IMAGE_COLLECTION'], condition={"eventId": eventId})
        if record:
            fileobj = '{}/{}/{}.jpg'.format(current_app.config['AWS_IMAGE_FOLDER_PREFIX'], eventId, imageId)
            client.delete_object(Bucket=current_app.config['BUCKET'], Key=fileobj)
            print('Image: {} for event {} deletion off of s3 successful'.format(imageId, eventId))
            return True
        else:
            print('Event: {} does not exist'.format(eventId))
            return False

    except Exception:
        traceback.print_exc()
        print("Image: {} for event: {} deletion failed".format(imageId, eventId))
        return False


def s3_image_upload(eventId, imageId):
    try:
        image_png_location = '{}/{}.png'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], eventId)
        # convert from png to jpg and save it
        with Image.open(image_png_location) as im:
            im.convert('RGB').save('{}/{}.jpg'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], eventId),
                                    quality=95)
        client.upload_file(
            '{}/{}.jpg'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], eventId),
            current_app.config['BUCKET'],
            '{}/{}/{}.jpg'.format(current_app.config['AWS_IMAGE_FOLDER_PREFIX'], eventId, imageId),
            ExtraArgs={
                'ACL': 'bucket-owner-full-control'
            }
        )
        success = True

    except Exception:
        traceback.print_exc()
        print("Upload image: {} for event {} failed".format(imageId, eventId))
        success = False
    finally:
        if os.path.exists('{}/{}.png'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], eventId)):
            os.remove('{}/{}.png'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], eventId))

        if os.path.exists('{}/{}.jpg'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], eventId)):
            os.remove('{}/{}.jpg'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], eventId))

        return success

def s3_image_download(eventId, imageId):
    try:
        record = find_one(current_app.config['IMAGE_COLLECTION'], condition={"eventId": eventId})
        if record:
            fileobj = '{}/{}/{}.jpg'.format(current_app.config['AWS_IMAGE_FOLDER_PREFIX'], eventId, imageId)
            tmpfolder = 'temp'
            if not os.path.isdir(tmpfolder):
                os.mkdir(tmpfolder)
            tmpfile = os.path.join(tmpfolder, eventId + ".jpg")
            with open(tmpfile, 'wb') as f:
                client.download_fileobj(current_app.config['BUCKET'], fileobj, f)
                print('Image: {} for event {} download off of s3 successful'.format(imageId, eventId))
                return True

        else:
            print('Event: {} does not exist'.format(eventId))
            return False

    except Exception:
        traceback.print_exc()
        deletefile(tmpfile)
        print("Image: {} for event: {} download failed".format(imageId, eventId))
        return False

def deletefile(tmpfile):
    try:
        if os.path.exists(tmpfile):
            os.remove(tmpfile)

    except Exception as ex:
        pass

def s3_delete_reupload(eventId, imageId):
    try:
        record = find_one(current_app.config['IMAGE_COLLECTION'], condition={"eventId": eventId})
        if record:
            s3_image_delete(eventId, imageId)
            s3_image_upload(eventId, imageId)
            return True
        else:
            print('Event: {} does not exist'.format(eventId))
            return False

    except Exception:
        traceback.print_exc()
        print("Image: {} for event: {} reupload edit failed".format(imageId, eventId))
        return False


def imagedId_from_eventId(eventId):
    try:
        record = find_one(current_app.config['IMAGE_COLLECTION'], condition={"eventId": eventId})
        if record:
            return record['eventId']
        else:
            print('Event: {} does not have associated image'.format(eventId))
            return False

    except Exception:
        traceback.print_exc()
        print("imageId retrieval for event: {} failed".format(eventId))
        return False
