from datetime import datetime, timedelta

from ..db import update_one

from .constants import CalName2Location, int2CalDB, tip4CalALoc, eventTypeMap

from flask import current_app

import xml.etree.ElementTree as ET
import googlemaps
import requests

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
def geturl(filename):
    with open(filename, "r") as urlFile:
        return urlFile.read().split("\n")


def download(url):
    if url is None:
        return None

    response = requests.get(url)
    if response.status_code != 200:
        print("Invalid URL link: {}".format(url))

    # content = response.text.replace("&gt;", ">").replace("&lt;", "<")
    content = response.text
    return content


def parse(content, gmaps):
    try:
        tree = ET.fromstring(content)
    except ET.ParseError as e:
        print("Parsing Error: {}".format(e))
        return None

    XML2JSON=[]

    for publicEvent in tree:
        if publicEvent.tag != "publicEventWS":
            print("There is a error arrangement in the structure")
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
    print("Get {} raw events".format(len(XML2JSON)))

    xmltoMongoDB = []

    for pe in XML2JSON:

        entry = dict()

        # Required Field
        entry['eventId'] = pe['eventId'] if 'eventId' in pe else ""
        entry['eventType'] = pe['eventType'] if 'eventType' in pe else ""
        if entry['eventType'] not in eventTypeMap:
            print("find unknown eventType: {}".format(entry['eventType']))
        else:
            entry['eventType'] = eventTypeMap[entry['eventType']]
        entry['sponsor'] = pe['sponsor'] if 'sponsor' in pe else ""
        entry['title'] = pe['title'] if 'title' in pe else ""
        entry['calendarId'] = pe['calendarId'] if 'calendarId' in pe else ""
        entry['sourceId'] = '0'
        entry['eventStatus'] = "disapproved"
        entry['allDay'] = False

        if pe['timeType'] == "START_TIME_ONLY":
            startDate = pe['startDate']
            startTime = pe['startTime']
            startDateObj = datetime.strptime(startDate + ' ' + startTime + '', '%m/%d/%Y %I:%M %p')
            endDate = pe['endDate']
            endDateObj = datetime.strptime(endDate + ' 11:59 pm', '%m/%d/%Y %I:%M %p')
            # Convert CDT to UTC (offset by 5 hours)
            entry['startDate'] = (startDateObj+timedelta(hours=5)).strftime('%Y-%m-%dT%H:%M:%S')
            entry['endDate'] = (endDateObj+timedelta(hours=5)).strftime('%Y-%m-%dT%H:%M:%S')

        if pe['timeType'] == "ALL_DAY":
            entry['allDay'] = True
            startDate = pe['startDate']
            endDate = pe['endDate']
            startDateObj = datetime.strptime(startDate + ' 12:00 am', '%m/%d/%Y %I:%M %p')
            endDateObj = datetime.strptime(endDate + ' 11:59 pm', '%m/%d/%Y %I:%M %p')
            # Convert CDT to UTC (offset by 5 hours)
            entry['startDate'] = (startDateObj+timedelta(hours=5)).strftime('%Y-%m-%dT%H:%M:%S')
            entry['endDate'] = (endDateObj+timedelta(hours=5)).strftime('%Y-%m-%dT%H:%M:%S')

        elif pe['timeType'] == "START_AND_END_TIME":
            startDate = pe['startDate']
            startTime = pe['startTime']
            endDate = pe['endDate']
            endTime = pe['endTime']
            startDateObj = datetime.strptime(startDate + ' ' + startTime, '%m/%d/%Y %I:%M %p')
            endDateObj = datetime.strptime(endDate + ' ' + endTime, '%m/%d/%Y %I:%M %p')
            # Convert CDT to UTC (offset by 5 hours)
            entry['startDate'] = (startDateObj+timedelta(hours=5)).strftime('%Y-%m-%dT%H:%M:%S')
            entry['endDate'] = (endDateObj+timedelta(hours=5)).strftime('%Y-%m-%dT%H:%M:%S')

        # Optional Field
        if 'description' in pe:
            if pe['description'] == '\n':
                entry['description'] = ''
            else:
                entry['description'] = pe['description']
        if 'titleURL' in pe:
            entry['titleURL'] = pe['titleURL']
        if 'speaker' in pe:
            entry['speaker'] = pe['speaker']
        if 'registrationURL' in pe:
            entry['registrationURL'] = pe['registrationURL']
        if 'cost' in pe:
            entry['cost'] = pe['cost']
        if 'topic' in pe:
            entry['tags'] = pe['topic']

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
            contact['firstName'] = pe['contactName'].split(' ')[0].rstrip(',')
            contact['lastName'] = pe['contactName'].split(' ')[1]
        if 'contactEmail' in pe:
            contact['email'] = pe['contactEmail']
        if 'contactPhone' in pe:
            contact['phone'] = pe['contactPhone']
        contacts.append(contact) if len(contact) != 0 else None
        if len(contacts) != 0:
            entry['contacts']= contacts

        # find geographical location
        if 'location' in pe:
            location = pe['location']
            calendarName = pe['calendarName']
            sponsor = pe['sponsor']
            
            (found, GeoInfo) = search_static_location(calendarName, sponsor, location)
            if found:
                entry['location'] = GeoInfo
            else:
                try:
                    GeoResponse = gmaps.geocode(address=location+',Urbana', components={'administrative_area': 'Urbana', 'country': "US"})
                except googlemaps.exceptions.ApiError as e:
                    print("API Key Error: {}".format(e))
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
        xmltoMongoDB.append(entry)
    print("Get {} parsed events".format(len(xmltoMongoDB)))
    return xmltoMongoDB


def store(documents):

    update = 0
    insert = 0
    for document in documents:
        result = update_one(current_app.config['EVENT_COLLECTION'], condition={'eventId': document['eventId']},
                            update={'$set': document}, upsert=True)
        if result.matched_count == result.modified_count:
            insert += 1
        else:
            update += 1
    return (insert, update)


def start():

    if "GOOGLE_KEY" not in current_app.config or current_app.config["GOOGLE_KEY"] is None:
        print("Google Key does not exist. Cannot perform parsing")
        return

    GOOGLEKEY = current_app.config['GOOGLE_KEY']
    
    try:
        gmaps = googlemaps.Client(key=GOOGLEKEY)
    except ValueError as e:
        print("Error in connecting Google Api: {}".format(e))
    
    update_in_total = 0
    insert_in_total = 0
    urls = geturl(current_app.config['EVENT_URLS'])
    for url in urls:
        try:
            rawEvents = download(url)
            if rawEvents is None:
                print("Invalid content in: {}".format(url))
                continue
            print("Begin parsing url: {}".format(url))
            parsedEvents = parse(rawEvents, gmaps)
            (insert, update) = store(parsedEvents)
            insert_in_total += insert
            update_in_total += update
            print("{} are updated, {} are inserted".format(update, insert))
        except Exception as e:
            print("There is exception {}, hidden in url: {}".format(e, url))
            continue
    print("DateTime: {}, overall parsing result: {} are updated, {} are inserted".format(
        datetime.utcnow(), update_in_total, insert_in_total
    ))

    
