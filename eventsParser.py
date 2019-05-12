from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from logging.handlers import RotatingFileHandler
import xml.etree.ElementTree as ET
import requests
import json
import os
import logging
import re
import sys

# set up logger globally and in flask, it can be done using app.logging
if not os.path.exists('logs'):
        os.mkdir('logs')
    
# CAUTION: logging message will not write to log file if its level is lower than file handler level
#          also it does not print to console if its level is less than root level
file_handler = RotatingFileHandler('logs/events.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s-URL:'%(url)s'-EventID: %(eventid)s"))
file_handler.setLevel(logging.ERROR)

xmlLogger = logging.getLogger('xmlParser')
xmlLogger.addHandler(file_handler)
xmlLogger.setLevel(logging.INFO)

# store metadata globally
GeoUrl = "https://nominatim.openstreetmap.org/search?"


def extractEventXMLandParse(results, url=None, jsonF='eventsExample.json'):

    if url is None:
        return None
    
    response = requests.get(url)

    # Response Code should be 200 (OK)
    if response.status_code != 200:
        xmlLogger.error("Invalid URL Link", extra={'url': url, 'eventid': None})
        return None
    
    # CAUTION: text involved decode, may need to consider it later. Content may be useful to
    # handle byte data like photo
    content = response.text

    content = content.replace("&gt;", ">").replace("&lt;", "<")

    try:
        tree = ET.fromstring(content)
    except:
        xmlLogger.error("Invalid XML data", extra={'url': url, 'eventid': None})
        return None
    
    XML2Json = []

    # extract all contents from publicEvents
    for publicEvent in tree:
        
        # check for publicEvent tag
        if publicEvent.tag != "publicEventWS":
            xmlLogger.warn("There is a new child tagName under root", extra={'url': url, 'eventid': None})
            continue
        
        eventDetail = {}
        for elem in publicEvent:
            
            # description's field does not have text but a series of bytes
            if elem.tag == "description":
                soup = BeautifulSoup(ET.tostring(elem), 'html.parser')
                eventDetail[elem.tag] = soup.get_text()

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

        # Required Field
        entry['eventId'] = pe['eventId'] if 'eventId' in pe else ""
        entry['eventType'] = pe['eventType'] if 'eventType' in pe else ""
        entry['sponsor'] = pe['sponsor'] if 'sponsor' in pe else ""
        entry['title'] = pe['title'] if 'title' in pe else ""

        # TODO: there is a field called "dateDisplay" that seems to define whether there is a date
        if pe['timeType'] == "START_TIME_ONLY":
            startDate = pe['startDate']
            startTime = pe['startTime']
            startDateObj = datetime.strptime(startDate+' '+startTime, '%m/%d/%Y %I:%M %p')

            endDate = pe['endDate']
            endDateObj = datetime.strptime(endDate+' 11:59 pm', '%m/%d/%Y %I:%M %p')
            
            entry['startDate'] = startDateObj.isoformat()
            entry['endDate'] = endDateObj.isoformat()

        if pe['timeType'] == "ALL_DAY":
            startDate = pe['startDate']
            endDate = pe['endDate']
            startDateObj = datetime.strptime(startDate+' 12:00 am', '%m/%d/%Y %I:%M %p')
            endDateObj = datetime.strptime(endDate+' 11:59 pm', '%m/%d/%Y %I:%M %p')
            entry['startDate'] = startDateObj.isoformat()
            entry['endDate'] = endDateObj.isoformat()

        elif pe['timeType'] == "START_AND_END_TIME":
            startDate = pe['startDate']
            startTime = pe['startTime']
            endDate = pe['endDate']
            endTime = pe['endTime']

            startDateObj = datetime.strptime(startDate+' '+startTime, '%m/%d/%Y %I:%M %p')
            endDateObj = datetime.strptime(endDate+' '+endTime, '%m/%d/%Y %I:%M %p')

            entry['startDate'] = startDateObj.isoformat()
            entry['endDate'] = endDateObj.isoformat()
        

        # Optional Field
        if 'description' in pe:
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
            entry['tag'] = pe['topic']

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
            contact['firstName'] = pe['contactName'].split(' ')[0]
            contact['lastName'] = pe['contactName'].split(' ')[1]
        if 'contactEmail' in pe:
            contact['email'] = pe['contactEmail']
        if 'contactPhone' in pe:
            contact['phone'] = pe['contactPhone']
        contacts.append(contact) if len(contact) != 0 else None
        if len(contacts) != 0:
            entry['contacts']= contacts

        # find geographical location
        # TODO: do it in re match and set some file to record special conditions
        if 'location' in pe:
            if ("Stage" in pe['location'] or "Studio" in pe['location']) and "Krannert Center" in pe['calendarName']:
                location = "Krannert Center for the Performing Arts"
            else:
                location = pe['location']+',UIUC'
        else:
            if "Krannert Center" in pe['calendarName']:
                location = "Krannert Center for the Performing Arts"
            else:
                location = ''


        QueryUrl = "{}{}".format(GeoUrl, urlencode({'q': location, 'format': 'json'}))
        GeoResponse = requests.get(QueryUrl)

        if GeoResponse.status_code != 200:
            xmlLogger.error("Invalid GeoURL Link", extra={'url': url, 'eventid': pe['eventid']})
        
        GeoContent = json.loads(GeoResponse.text)
        if len(GeoContent) != 0:
            GeoInfo = {}
            GeoInfo['latitude'] = GeoContent[0]['lat']
            GeoInfo['longitude'] = GeoContent[0]['lon']
            GeoInfo['description'] = GeoContent[0]['display_name']
            entry['location'] = GeoInfo


        xmltoMongoDB.append(entry)
    
    return xmltoMongoDB

    
def parseEventXML(xml='eventsExample.txt', jsonF='eventsExample.json'):

    with open(xml, "r") as sample:
        content = sample.read()

    tree = ET.fromstring(content)

    XML2Json = []

        


if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print("Usage: python eventsParser.py urls_file json_file")
        print("       urls_file: file that contains events urls separated by newline")
        print("       json_file: file that stores parsed result")
        exit()

    urls_file = sys.argv[1]
    json_file = sys.argv[2]
    parseResult = []
    with open(urls_file, "r") as urlsList:
        urls = urlsList.read().split("\n")

    for url in urls:
        parseResult = parseResult + extractEventXMLandParse(parseResult, url=url, jsonF=json_file)
    
    with open(json_file, 'w') as parseContainer:
        json.dump(parseResult, parseContainer, indent='\t')


