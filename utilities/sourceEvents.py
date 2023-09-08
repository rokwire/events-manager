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
import boto3
from datetime import datetime, timedelta

from ..db import update_one, replace_one, find_one, insert_one, find_all_previous_event_ids
from ..config import Config
from .constants import CalName2Location, tip4CalALoc, eventTypeMap
from .downloadImage import downloadImage
from .source_utilities import get_all_calendar_status, publish_event, s3_publish_image, delete_events
from flask import current_app
from .constants import *
from . import event_time_conversion
import xml.etree.ElementTree as ET
import googlemaps
import requests
import traceback
import logging
from time import gmtime
logging.Formatter.converter = gmtime
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%dT%H:%M:%S',
                    format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s [%(threadName)-10s] : %(name)s - %(message)s')
__logger = logging.getLogger("sourceEvents.py")

######################################################################
### parsing helper functions
######################################################################

# this function is used for providing a customed geoinformation when
# google API can not be utilized. For example, in Krannert Art Center
# events, studio 5 and stage 5 are often appeared which by API, they
# points to different unrelated location in Champaign. These conditions
# are rare and for now, this function will search for keywords in location
# description and combine with calendar name to find the mapped geoinfo
def search_static_location(calendarName, sponsor, location):
    for tip in tip4CalALoc:
        if calendarName==tip[0] and ((tip[1] in sponsor.lower()) and (tip[2] in location.lower())):
            GeoInfo = {
                'latitude': CalName2Location[tip[3]][0],
                'longitude': CalName2Location[tip[3]][1],
                'description': location,
            }
            return (True, GeoInfo)
    return (False, None)


######################################################################
### Normal parse process functions
######################################################################
def geturls(targets):
    urls = []
    if targets is None:
        for eventMap in current_app.config['INT2SRC']['0'][1]:
            urls.append("{}{}{}".format(current_app.config['EVENT_URL_PREFIX'], list(eventMap.keys())[0], current_app.config['EVENT_URL_SUFFIX']))
    else:
        for target in targets:
            urls.append("{}{}{}".format(current_app.config['EVENT_URL_PREFIX'], target, current_app.config['EVENT_URL_SUFFIX']))

    return urls

def download(url):
    if url is None:
        return None

    response = requests.get(url)
    if response.status_code != 200:
        __logger.error("Invalid URL link: {}".format(url) + ", response.status_code: %d" % response.status_code)

    # content = response.text.replace("&gt;", ">").replace("&lt;", "<")
    content = response.text
    return content


def parse(content, gmaps):
    try:
        tree = ET.fromstring(content)
    except ET.ParseError as e:
        __logger.error("Parsing Error: {}".format(e))
        return []

    XML2JSON=[]
    for publicEvent in tree:
        if publicEvent.tag != "publicEventWS":
            __logger.error("There is a error arrangement in the structure")
            continue

        eventDetail = {}
        for elem in publicEvent:
            if elem.tag == "description":
                if len(elem) < 1:
                    if elem.text is None:
                        continue
                    eventDetail[elem.tag] = elem.text
                else:
                    eventDetail[elem.tag] = ET.tostring(elem[0])
            elif elem.tag == "topic":
                if 'topic' in eventDetail:
                    eventDetail['topic'].append(elem[1].text)
                else:
                    eventDetail['topic'] = [elem[1].text]
            elif elem.text is None:
                continue

            else:
                eventDetail[elem.tag] = elem.text

        XML2JSON.append(eventDetail)
    __logger.info("Get {} raw events".format(len(XML2JSON)))

    xmltoMongoDB = []
    notSharedWithMobileList = []

    for pe in XML2JSON:
        # decide not to skip if location not exist or empty.
        # if not pe.get('location'):
        #     continue
        entry = dict()
        entry['category'] = pe['eventType'] if 'eventType' in pe else ""
        if entry['category'] not in eventTypeMap:
            __logger.warning("Found unknown eventType: {}".format(entry['category']))
            # Exclude events from WebTools with certain categories
            continue
        else:
            entry['category'] = eventTypeMap[entry['category']]

        if pe['timeType'] == "ALL_DAY":
            # skip all day event. (https://github.com/rokwire/events-manager/issues/1086)
            continue
            
        entry['originatingCalendarId'] = pe['originatingCalendarId']
        if pe.get("shareWithIllinoisMobileApp", "false") == "false":
            dataSourceEventId = pe.get("eventId", "")
            result = find_one(
                current_app.config['EVENT_COLLECTION'], 
                condition={'dataSourceEventId': dataSourceEventId}
            )
            if result:
                notSharedWithMobileList.append(result["_id"])
            continue

        if pe.get("virtualEvent", "false") == "true":
            entry['isVirtual'] = True
        else:
            entry['isVirtual'] = False
        if 'virtualEventURL' in pe:
            entry['virtualEventUrl'] = pe['virtualEventURL']
        if 'inPersonEvent' in  pe:
            if pe['inPersonEvent'] == "true":
                entry['isInPerson'] = True
            else:
                entry['isInPerson'] = False

        # Required Field
        entry['dataSourceEventId'] = pe['eventId'] if 'eventId' in pe else ""
        # entry['eventId'] = pe['eventId'] if 'eventId' in pe else ""
        entry['sponsor'] = pe['sponsor'] if 'sponsor' in pe else ""
        entry['title'] = pe['title'] if 'title' in pe else ""
        entry['calendarId'] = pe['calendarId'] if 'calendarId' in pe else ""
        entry['sourceId'] = '0'
        entry['allDay'] = False

        if 'costFree' in pe:
            if pe.get('costFree') == "true":
                entry['isEventFree'] = True
            if pe.get('costFree') == "false":
                entry['isEventFree'] = False

        # find geographical location
        skip_google_geoservice = False
        if not pe.get('location'):
            skip_google_geoservice = True
        # flag for checking online event
        found_online_event = False
        # compare with the existing location
        existing_event = find_one(current_app.config['EVENT_COLLECTION'], condition={'dataSourceEventId': entry[
            'dataSourceEventId'
        ]})
        existing_location = existing_event.get('location')

        # filter out online location
        if pe.get('location'):
            pe_location_lower_case = pe["location"].lower()
            for excluded_location in Config.EXCLUDED_LOCATION:
                if excluded_location.lower() in pe_location_lower_case:
                    skip_google_geoservice = True
                    found_online_event = True
                    entry["location"] = {
                        "description": pe["location"]
                    }
                    break

        if existing_location:
            # mark previouly unidentified online events
            if found_online_event:
                if existing_location.get('latitude') and existing_location.get('longitude'):
                    entry["replace_event"] = True
            else:
                existing_description = existing_location.get('description')
                if existing_description == pe.get('location'):
                    if existing_location.get('latitude') and existing_location.get('longitude'):
                        skip_google_geoservice = True
                        lat = existing_location.get('latitude')
                        lng = existing_location.get('longitude')
                        GeoInfo = {
                            'latitude': lat,
                            'longitude': lng,
                            'description': pe['location']
                        }
                        entry['location'] = GeoInfo

        if not entry.get('isVirtual') or not skip_google_geoservice:
            location = pe.get('location')
            calendarName = pe['calendarName']
            sponsor = pe['sponsor']

            if location in predefined_locations:
                entry['location'] = predefined_locations[location]
                __logger.info("assign predefined geolocation: calendarId: " + str(entry['calendarId']) + ", dataSourceEventId: " + str(entry['dataSourceEventId']))
            elif location:
                (found, GeoInfo) = search_static_location(calendarName, sponsor, location)
                if found:
                    entry['location'] = GeoInfo
                else:
                    try:
                        GeoResponse = gmaps.geocode(address=location+',Urbana', components={'administrative_area': 'Urbana', 'country': "US"})
                    except googlemaps.exceptions.ApiError as e:
                        __logger.error("API Key Error: {}".format(e))
                        entry['location'] = {'description': pe['location']}
                        xmltoMongoDB.append(entry)
                        continue

                    if len(GeoResponse) != 0:
                        lat = GeoResponse[0]['geometry']['location']['lat']
                        lng = GeoResponse[0]['geometry']['location']['lng']
                        GeoInfo = {
                            'latitude': lat,
                            'longitude': lng,
                            'description': pe['location']
                        }
                        entry['location'] = GeoInfo
                    else:
                        entry['location'] = {'description': pe['location']}
                        __logger.error("calendarId: %s, dataSourceEventId: %s,  location: %s geolocation not found" %
                              (entry.get('calendarId'), entry.get('dataSourceEventId'), entry.get('location')))
            else:
                entry['location'] = {
                            'description': ""
                        }
        else:
            entry['location'] = {
                'description': ""
            }
        entry_location = entry['location']
        if pe['timeType'] == "START_TIME_ONLY":
            startDate = pe['startDate']
            startTime = pe['startTime']
            startDateObj = datetime.strptime(startDate + ' ' + startTime + '', '%m/%d/%Y %I:%M %p')
            endDate = pe['endDate']
            endDateObj = datetime.strptime(endDate + ' 11:59 pm', '%m/%d/%Y %I:%M %p')
            # normalize event datetime to UTC
            # TODO: current default time zone is CDT
            entry['startDate'] = event_time_conversion.utctime(startDateObj, entry_location.get('latitude', 40.1153287), entry_location.get('longitude', -88.2280659))
            entry['endDate'] = event_time_conversion.utctime(endDateObj, entry_location.get('latitude', 40.1153287), entry_location.get('longitude', -88.2280659))

        elif pe['timeType'] == "START_AND_END_TIME":
            startDate = pe['startDate']
            startTime = pe['startTime']
            endDate = pe['endDate']
            endTime = pe['endTime']
            startDateObj = datetime.strptime(startDate + ' ' + startTime, '%m/%d/%Y %I:%M %p')
            endDateObj = datetime.strptime(endDate + ' ' + endTime, '%m/%d/%Y %I:%M %p')
            # normalize event datetime to UTC
            # TODO: current default time zone is CDT
            entry['startDate'] = event_time_conversion.utctime(startDateObj, entry_location.get('latitude', 40.1153287), entry_location.get('longitude', -88.2280659))
            entry['endDate'] = event_time_conversion.utctime(endDateObj, entry_location.get('latitude', 40.1153287), entry_location.get('longitude', -88.2280659))

        # when time type is None, usually happens in calendar 468
        elif pe['timeType'] == "NONE":
            entry['allDay'] = True
            startDate = pe['startDate']
            endDate = pe['endDate']
            startDateObj = datetime.strptime(startDate + ' 12:00 am', '%m/%d/%Y %I:%M %p')
            endDateObj = datetime.strptime(endDate + ' 11:59 pm', '%m/%d/%Y %I:%M %p')
            # normalize event datetime to UTC
            # TODO: current default time zone is CDT
            entry['startDate'] = event_time_conversion.utctime(startDateObj, entry_location.get('latitude', 40.1153287), entry_location.get('longitude', -88.2280659))
            entry['endDate'] = event_time_conversion.utctime(endDateObj, entry_location.get('latitude', 40.1153287), entry_location.get('longitude', -88.2280659))

        # Optional Field
        if 'description' in pe:
            if pe['description'] == '\n':
                entry['longDescription'] = ''
            else:
                entry['longDescription'] = pe['description']
        if 'titleURL' in pe:
            entry['titleURL'] = pe['titleURL']
        if 'speaker' in pe:
            entry['speaker'] = pe['speaker']
        if 'registrationURL' in pe:
            entry['registrationURL'] = pe['registrationURL']
        if 'registrationLabel' in pe:
            entry['registrationLabel'] = pe['registrationLabel']
        if 'cost' in pe:
            entry['cost'] = pe['cost']
        if 'topic' in pe:
            entry['tags'] = pe['topic']
        if 'recurrence' in pe:
            if pe['recurrence'] == "false":
                entry['recurringFlag'] = False
            else:
                entry['recurringFlag'] = True
        if 'recurrenceId' in pe:
            entry['recurrenceId'] = int(pe['recurrenceId'])

        entry['icalUrl'] = "https://calendars.illinois.edu/ical/{}/{}.ics".format(pe['calendarId'], pe['eventId'])
        entry['outlookUrl'] = "https://calendars.illinois.edu/outlook2010/{}/{}.ics".format(pe['calendarId'],
                                                                                            pe['eventId'])

        targetAudience = []
        targetAudience.extend(["faculty", "staff"]) if pe['audienceFacultyStaff'] == "true" else None
        targetAudience.append("students") if pe['audienceStudents'] == "true" else None
        targetAudience.append("public") if pe['audiencePublic'] == "true" else None
        targetAudience.append("alumni") if pe['audienceAlumni'] == "true" else None
        targetAudience.append("parents") if pe['audienceParents'] == "true" else None
        if len(targetAudience) != 0:
            entry['targetAudience'] = targetAudience

        contacts = []
        contact = {}
        if 'contactName' in pe:
            name_list = pe['contactName'].split(' ')
            contact['firstName'] = pe['contactName'].split(' ')[0].rstrip(',')
            if len(name_list) > 1:
                contact['lastName'] = pe['contactName'].split(' ')[1]
            else:
                contact['lastName'] = ""
        if 'contactEmail' in pe:
            contact['email'] = pe['contactEmail']
        if 'contactPhone' in pe:
            contact['phone'] = pe['contactPhone']
        contacts.append(contact) if len(contact) != 0 else None
        if len(contacts) != 0:
            entry['contacts']= contacts

        # creation information
        dateCreatedObj = datetime.strptime(pe['createdDate'] + ' 12:00 am', '%m/%d/%Y %I:%M %p')
        entry['dateCreated'] = (dateCreatedObj+timedelta(hours=5)).strftime('%Y-%m-%dT%H:%M:%S')
        if 'createdBy' in pe:
            entry['createdBy'] = pe['createdBy']

        # edit information
        dataModifiedObj = datetime.strptime(pe['editedDate'] + ' 12:00 am', '%m/%d/%Y %I:%M %p')
        entry['dataModified'] = (dataModifiedObj+timedelta(hours=5)).strftime('%Y-%m-%dT%H:%M:%S')

        xmltoMongoDB.append(entry)
    __logger.info("Get {} parsed events".format(len(xmltoMongoDB)))
    __logger.info("Get {} not shareWithIllinoisMobileApp events".format(len(notSharedWithMobileList)))
    return (xmltoMongoDB, notSharedWithMobileList)


def store(documents):

    calendarStatus = get_all_calendar_status()

    update = 0
    insert = 0
    post = 0
    put = 0
    patch = 0
    delete = 0
    unknown = 0

    image_download = 0
    image_upload = 0

    for document in documents:
        result = find_one(current_app.config['EVENT_COLLECTION'], condition={'dataSourceEventId': document[
            'dataSourceEventId'
        ]})

        # if it is a new event
        if not result:
            document['submitType'] = 'post'
            calendarId = document['calendarId']
            calendar_status = calendarStatus.get(calendarId)

            # if calendar is disapproved
            if calendar_status.get('status') == "disapproved":
                document['eventStatus'] = 'disapproved'

            # if calendar is approved
            elif calendar_status.get('status') == 'approved':
                document['eventStatus'] = 'approved'

            # if calendar status is unknown
            else:
                document['eventStatus'] = 'pending'

            insert_result = insert_one(current_app.config['EVENT_COLLECTION'], document=document)
            # insert error condition check
            if insert_result.inserted_id is None:
                __logger.error("Insert event {}  of calendar {} failed in start".format(document['dataSourceEventId'], calendarId))
            else:
                document['eventId'] = str(insert_result.inserted_id)
                insert += 1

        # if it is an existing event
        else:
            # In event replacement, eventStatus, eventId and platformEventId(when event is published) will 
            # not be contained in parsed events. 
            document["eventStatus"] = result['eventStatus']
            document["eventId"] = result["eventId"]
            # TODO: The following IF condition is a temporary fix to make sure that the current data is updated. It can
            #  be removed later.
            if result.get('submitType') == 'post' and result.get('eventStatus') == 'pending':
                document['submitType'] = 'post'
                document['eventStatus'] = 'approved'
            elif result['eventStatus'] == 'published':
                document['submitType'] = 'put'
                document["platformEventId"] = result["platformEventId"]
            update += 1

        # if this event is marked as replacement
        if document.get("replace_event", False):
            del document["replace_event"]
            replaceResult = replace_one(
                current_app.config['EVENT_COLLECTION'], 
                condition={'dataSourceEventId': document['dataSourceEventId']}, 
                replacement=document,
                upsert=True,
            )
            # insert replace error check
            if replaceResult.modified_count == 0 and replaceResult.matched_count == 0 and replaceResult.upserted_id is None:
                __logger.error("replace event {} of calendar {} fails in start".format(document['dataSourceEventId'], calendarId))
        else:
            updateResult = update_one(current_app.config['EVENT_COLLECTION'], condition={'dataSourceEventId': document['dataSourceEventId']},
                    update={'$set': document}, upsert=True)
            # insert update error check
            if updateResult.modified_count == 0 and updateResult.matched_count == 0 and updateResult.upserted_id is None:
                __logger.error("update event {} of calendar {} fails in start".format(document['dataSourceEventId'], calendarId))

    s3_client = boto3.client('s3')
    # upload approved or published events
    for document in documents:
        result = find_one(current_app.config['EVENT_COLLECTION'], condition={'dataSourceEventId': document[
            'dataSourceEventId'
        ]})

        if result:
            event_status = result.get('eventStatus')
            # if event is approved or published
            if event_status == 'approved' or event_status == 'published':
                # for image accessing here, we first attempt to download image and if there is indeed an
                # image in existence. We, then, try to upload the image.
                imageId = None
                if downloadImage(result['originatingCalendarId'], result['dataSourceEventId'], result['eventId']):
                    image_download += 1

                event_upload_success, imageId = publish_event(result['eventId'])
                if event_upload_success:
                    if imageId:
                        image_upload += 1

                    if result['submitType'] == 'post':
                        post += 1
                    elif result['submitType'] == 'put':
                        put +=1
                    elif result['submitType'] == 'patch':
                        patch += 1
                    elif result['submitType'] == 'delete':
                        delete +=1
                    else:
                        unknown += 1
        else:
            __logger.error("find event {} from calendar {} fails in start".format(document['dataSourceEventId'],
                                                                         document['calendarId']))
    return (insert, update, post, put, patch, unknown, image_download, image_upload)

def get_difference_old_new(new_eventId_list, previous_eventId_list):
    if new_eventId_list is None or previous_eventId_list is None:
        return []
    difference = []
    for old_event_ids in previous_eventId_list:
        if old_event_ids['dataSourceEventId'] not in new_eventId_list:
           difference.append(old_event_ids['_id'])
    return difference

def start(targets=None):

    if "GOOGLE_KEY" not in current_app.config or current_app.config["GOOGLE_KEY"] is None:
        __logger.error("Google Key does not exist. Cannot perform parsing")
        return

    GOOGLEKEY = current_app.config['GOOGLE_KEY']

    try:
        gmaps = googlemaps.Client(key=GOOGLEKEY)
    except ValueError as e:
        __logger.error("Error in connecting Google Api: {}".format(e))

    parsed_in_total = 0
    update_in_total = 0
    insert_in_total = 0
    upload_in_total = 0
    post_in_total = 0
    put_in_total = 0
    patch_in_total = 0
    delete_in_total = 0
    unknown_in_total = 0

    image_download_total = 0
    image_upload_total = 0

    #getting new event id's
    new_eventId_list = []

    # get all previous event ids from db
    previous_eventId_list = find_all_previous_event_ids(current_app.config['EVENT_COLLECTION'], filter={"dataSourceEventId": {'$exists': 'true'}})
    urls = geturls(targets)
    for url in urls:
        parsedEvents = list()
        notShareWithMobileList = list()
        try:
            page_number = 0
            while True:
                pagination_url = url + "?pageNumber=%d" % page_number
                rawEvents = download(pagination_url)
                if rawEvents is None:
                    __logger.error("Invalid content in: {}".format(pagination_url))
                __logger.info("Begin parsing url: {}".format(pagination_url))
                parsedEvents_iteration, notShareWithMobileList_iteration = parse(rawEvents, gmaps)
                parsedEvents.extend(parsedEvents_iteration)
                notShareWithMobileList.extend(notShareWithMobileList_iteration)
                if not parsedEvents_iteration:
                    __logger.error("Stop downloading and parsing on url: {}".format(pagination_url))
                    break
                page_number += 1

            if not parsedEvents:
                continue

            #getting new event id's
            for event_current in parsedEvents:
                new_eventId_list.append(event_current['dataSourceEventId'])

            parsed_in_total += len(parsedEvents)
            (insert, update, post, put, patch, unknown, image_download, image_upload) = store(parsedEvents)

            upload_in_total += post + put + patch + unknown
            insert_in_total += insert
            update_in_total += update
            post_in_total   += post
            put_in_total    += put
            patch_in_total  += patch
            unknown_in_total += unknown
            image_download_total += image_download
            image_upload_total += image_upload

            __logger.info(
                "".join([
                    "EventManager: {} are updated, {} are inserted.\n".format(update, insert),
                    "Event Building Block: {} are posted, {} are put, {} are patch, {} are unknown\n".format(post, put, patch, unknown)
                ])
            )
            __logger.info("Regarding to images: {} are downloaded, {} are uploaded\n".format(image_download, image_upload))

        except Exception as ex:
            __logger.error("There is exception {}, hidden in url: {}".format(ex, url))
            continue

    #compare old events in db, new downloads, find difference to delete
    __logger.info("# new_eventId_list: " + str(len(new_eventId_list)))
    __logger.info("# previous_eventId_list: " + str(len(previous_eventId_list)))
    previous_events_to_delete = get_difference_old_new(new_eventId_list, previous_eventId_list)
    __logger.info("# previous_events_to_delete: " + str(len(previous_events_to_delete)))
    deletion = delete_events(previous_events_to_delete)

    __logger.info(
        "".join([
            "DateTime: {}, overall parsing result: {} events\n".format(datetime.utcnow(), parsed_in_total),
            "    Updated: {}\n".format(update_in_total),
            "    Inserted: {}\n".format(insert_in_total),
            "Overall uploading result: {} events\n".format(upload_in_total),
            "    Post: {}\n".format(post_in_total),
            "    Put: {}\n".format(put_in_total),
            "    Patch: {}\n".format(patch_in_total),
            "    Unknown: {}\n".format(unknown_in_total),
        ])
    )
    __logger.info(
        "".join([
            "Total images downloaded are: {}\n".format(image_download_total),
            "Total images uploaded are: {}\n".format(image_upload_total)
        ])
    )

