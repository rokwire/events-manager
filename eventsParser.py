from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from logging import FileHandler
from dotenv import load_dotenv
from constants import CalName2Location, int2CalDB, tip4CalALoc
import xml.etree.ElementTree as ET
import googlemaps 
import requests
import json
import os
import logging
import re
import sys


# 1. add schema fields: events status
# 2. fill out floor
# 3. 


# set up logger globally and in flask, it can be done using app.logging
if not os.path.exists('logs'):
        os.mkdir('logs')

# load subtle information
load_dotenv()

# CAUTION: logging message will not write to log file if its level is lower than file handler level
#          also it does not print to console if its level is less than root level
file_handler = FileHandler('logs/events.log')
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s-URL:'%(url)s'-EventID: %(eventid)s"))
file_handler.setLevel(logging.INFO)

xmlLogger = logging.getLogger('xmlParser')
xmlLogger.addHandler(file_handler)
xmlLogger.setLevel(logging.INFO)

# store metadata globally
GeoUrl = "https://nominatim.openstreetmap.org/search?"
GOOGLEKEY= os.getenv('GOOGLEKEY')
gmaps = googlemaps.Client(key=GOOGLEKEY)



def extractEventXMLandParse(provided_file=None, url=None):

    if url is None and provided_file is None:
        return None
    
    if url is not None:
        response = requests.get(url)
        # Response Code should be 200 (OK)
        if response.status_code != 200:
            xmlLogger.error("Invalid URL Link", extra={'url': url, 'eventid': None})
            return None
        
        # CAUTION: text involved decode, may need to consider it later. Content may be useful to
        # handle byte data like photo
        content = response.text
        content = content.replace("&gt;", ">").replace("&lt;", "<")
    else:
        with open(provided_file, 'r') as source:
            content = source.read()
    
    try:
        tree = ET.fromstring(content)
    except:
        xmlLogger.error("Invalid XML data", extra={'url': url, 'eventid': None})
        return None
    
    xmlLogger.info("Found {} events".format(len(tree)), extra={'url': url, 'eventid': None})

    XML2Json = []

    # extract all contents from publicEvents
    for publicEvent in tree:
        
        # check for publicEvent tag
        if publicEvent.tag != "publicEventWS":
            xmlLogger.error("There is a new child tagName under root", extra={'url': url, 'eventid': None})
            continue
        
        eventDetail = {}
        for elem in publicEvent:
            
            # # description's field does not have text but a series of bytes
            # if elem.tag == "description":
            #     try:
            #         soup = BeautifulSoup(ET.tostring(elem), 'html.parser')
            #     except Exception:
            #         xmlLogger.error("Error parsing html content under descriptions", extra={'url': url, 'eventid': publicEvent['eventId']})
            #     eventDetail[elem.tag] = soup.get_text()
            if elem.tag == "description":
                if len(elem) < 1:
                    if elem.text is None:
                        continue
                    eventDetail[elem.tag] = elem.text.decode('utf-8')
                else:
                    eventDetail[elem.tag] = ET.tostring(elem[0]).decode('utf-8')

            # it is possible that there are multiple topic tags in existence
            elif elem.tag == "topic":
                if 'topic' in eventDetail:
                    eventDetail['topic'].append(elem[1].text)
                else:
                    eventDetail['topic'] = [elem[1].text]
            

            elif elem.text == None:
                continue
            
            else:
                eventDetail[elem.tag] = elem.text
            

        XML2Json.append(eventDetail)


    # modify datetime format in XML, change it from 'MM/DD/YYYY HH/MIN' to 'DD/MM/YYYY HH/MIN/SS'
    # if endtime is not defined, then 
    #   if endDate is the same day as startDate, endtime will be defaultly set to 1 hour later
    #   if different, endtime will be set to 1 day after starttime

    xmltoMongoDB = []

    # TODO: test whether mongoDB allows field to be not specifically defined in json while passing
    for pe in XML2Json:

        entry = {}
        xmlLogger.info("Checking requests", extra={'url': url, 'eventid': pe['eventId']})

        # Required Field
        entry['eventId'] = pe['eventId'] if 'eventId' in pe else ""
        entry['eventType'] = pe['eventType'] if 'eventType' in pe else ""
        entry['sponsor'] = pe['sponsor'] if 'sponsor' in pe else ""
        entry['title'] = pe['title'] if 'title' in pe else ""
        entry['calendarId'] = pe['calendarId'] if 'calendarId' in pe else ""
        entry['sourceId'] = '0'
        entry['eventStatus'] = "incomplete"
        entry['allDay'] = False
        

        if pe['timeType'] == "START_TIME_ONLY":
            startDate = pe['startDate']
            startTime = pe['startTime']
            startDateObj = datetime.strptime(startDate+' '+startTime, '%m/%d/%Y %I:%M %p')

            endDate = pe['endDate']
            endDateObj = datetime.strptime(endDate+' 11:59 pm', '%m/%d/%Y %I:%M %p')
            
            entry['startDate'] = startDateObj.strftime('%Y/%m/%dT%H:%M:%S')
            entry['endDate'] = endDateObj.strftime('%Y/%m/%dT%H:%M:%S')

        if pe['timeType'] == "ALL_DAY":
            entry['allDay'] = True
            startDate = pe['startDate']
            endDate = pe['endDate']
            startDateObj = datetime.strptime(startDate+' 12:00 am', '%m/%d/%Y %I:%M %p')
            endDateObj = datetime.strptime(endDate+' 11:59 pm', '%m/%d/%Y %I:%M %p')
            entry['startDate'] = startDateObj.strftime('%Y/%m/%dT%H:%M:%S')
            entry['endDate'] = endDateObj.strftime('%Y/%m/%dT%H:%M:%S')

        elif pe['timeType'] == "START_AND_END_TIME":
            startDate = pe['startDate']
            startTime = pe['startTime']
            endDate = pe['endDate']
            endTime = pe['endTime']

            startDateObj = datetime.strptime(startDate+' '+startTime, '%m/%d/%Y %I:%M %p')
            endDateObj = datetime.strptime(endDate+' '+endTime, '%m/%d/%Y %I:%M %p')

            entry['startDate'] = startDateObj.strftime('%Y/%m/%dT%H:%M:%S')
            entry['endDate'] = endDateObj.strftime('%Y/%m/%dT%H:%M:%S')
        

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
        entry['outlookUrl'] = "https://calendars.illinois.edu/outlook2010/{}/{}.ics".format(pe['calendarId'], pe['eventId'])

        targetAudience = []
        targetAudience.extend(["faculty", "staff"]) if pe['audienceFacultyStaff'] == True else None
        targetAudience.append("students") if pe['audienceStudents'] == True else None
        targetAudience.append("public") if pe['audiencePublic'] == True else None
        targetAudience.append("alumni") if pe['audienceAlumni'] == True else None
        targetAudience.append("parents") if pe['audienceParents'] == True else None
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
            found = 0
            for tip in tip4CalALoc:
                if (calendarName == tip[0]) and ((tip[1] in sponsor.lower()) and (tip[2] in location.lower())):
                    GeoInfo = {
                        'latitude': CalName2Location[tip[3]][0],
                        'longitude': CalName2Location[tip[3]][1],
                        'description': pe['location']
                    }
                    entry['location'] = GeoInfo
                    found = 1
                    break
            
            if found == 0:
                try:
                    GeoResponse = gmaps.geocode(address=location+',Urbana', components={'administrative_area': 'Urbana', 'country': "US"})
                except Exception:
                    xmlLogger.error("Error Accessing Google Geocoding", extra={'url': url, 'eventid': pe['eventid']})

                # QueryUrl = "{}{}".format(GeoUrl, urlencode({'q': location, 'format': 'json'}))
                # GeoResponse = requests.get(QueryUrl)

                # if GeoResponse.status_code != 200:
                #     xmlLogger.error("Invalid GeoURL Link", extra={'url': url, 'eventid': pe['eventid']})
                
                # GeoContent = json.loads(GeoResponse.text)
                if len(GeoResponse) != 0:
                    # # for now, since app is applied to Urbana, Champaign range, latitude and longitude are ranged
                    # if lat < 42 and lat > 40 and lon < -87 and lon > -89:
                    #     GeoInfo = {}
                    #     GeoInfo['latitude'] = lat
                    #     GeoInfo['longitude'] = lon
                    #     GeoInfo['description'] = pe['location']
                    #     entry['location'] = GeoInfo
                    # else:
                    #     entry['location'] = {'description': pe['location']}
                    
                    lat = GeoResponse[0]['geometry']['location']['lat']
                    lng = GeoResponse[0]['geometry']['location']['lng']
                    # This location means UIUC in general
                    if lat == 40.1019523 and lng == -88.2271615:
                        if len(CalName2Location[calendarName]) != 0:
                            GeoInfo = {
                                'latitude': CalName2Location[calendarName][0],
                                'longitude': CalName2Location[calendarName][1],
                                'description': pe['location']
                            }
                            entry['location'] = GeoInfo
                        else:
                            entry['location'] = {'description': pe['location']}
                    else:
                        GeoInfo = {
                            'latitude': GeoResponse[0]['geometry']['location']['lat'],
                            'longitude': GeoResponse[0]['geometry']['location']['lng'],
                            'description': pe['location']
                        }
                        entry['location'] = GeoInfo
                    

        xmltoMongoDB.append(entry)
    
    xmlLogger.info("Parsed {} events".format(len(xmltoMongoDB)), extra={'url': url, 'eventid': None})
    return xmltoMongoDB

    
def accessEventXML(store, url):

    if url is None:
        return None

    response = requests.get(url)

    # Response Code should be 200 (OK)
    if response.status_code != 200:
        xmlLogger.error("Invalid URL Link", extra={'url': url, 'eventid': None})
        return None


    with open(store, "a") as sample:
        sample.write(response.text.replace("&gt;", ">").replace("&lt;", "<"))

        


if __name__ == "__main__":
    
    if len(sys.argv) != 4:
        print("Usage: python eventsParser.py -g|-e|-f urls_file|xml_file store_file|json_file")
        print("       -g: get raw XML contents")
        print("       urls_file: file that contains events urls separated by newline")
        print("       store_file: file that stores raw material")
        print("       -e: extract events information from urls")
        print("       urls_file: file that contains events urls separated by newline")
        print("       json_file: json file that stores parsed results")
        print("       -f: extract events information from xml file")
        print("       xml_file: file that stores events in xml format")
        print("       json_file: json file that stores parsed results")
        exit()

    option = sys.argv[1]
    if option == '-e':
        urls_file = sys.argv[2]
        json_file = sys.argv[3]
        parseResult = []
        with open(urls_file, "r") as urlsList:
            urls = urlsList.read().split("\n")
        
        with open('logs/events.log', 'w'):
            pass

        for url in urls:
            parseResult = parseResult + extractEventXMLandParse(url=url)
        
        with open(json_file, 'w') as parseContainer:
            json.dump(parseResult, parseContainer, indent='\t')

        file_handler.close()

    elif option == '-g':

        urls_file = sys.argv[2]
        store_file = sys.argv[3]

        with open(urls_file, "r") as urlsList:
            urls = urlsList.read().split("\n")
        
        with open(store_file, "w") as storeFile:
            pass
        
        for url in urls:
            accessEventXML(store_file, url)

    elif option == '-f':

        xml_file = sys.argv[2]
        json_file = sys.argv[3]

        with open('logs/events.log', 'w'):
            pass
        
        parseResult = extractEventXMLandParse(provided_file=xml_file)
        with open(json_file, 'w') as parseContainer:
            json.dump(parseResult, parseContainer, indent='\t')

        file_handler.close()
