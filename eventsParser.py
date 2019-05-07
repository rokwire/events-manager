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


def extractEventXMLandParse(url=None, jsonF='eventsExample.json'):

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

            elif elem.tag == "topic":
                eventDetail[elem.tag] = elem[1].text

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
        entry['eventType'] = pe['eventType'] if 'eventType' in pe else ""
        entry['sponsor'] = pe['sponsor'] if 'sponsor' in pe else ""
        entry['title'] = pe['title'] if 'title' in pe else ""

        # TODO: there is a field called "dateDisplay" that seems to define whether there is a date
        if pe['timeType'] == "START_TIME_ONLY":
            startDate = pe['startDate']
            startTime = pe['startTime']
            startDateObj = datetime.strptime(startDate+' '+startTime, '%m/%d/%Y %I:%M %p')

            endDate = pe['endDate']
            if endDate == startDate:
                endDateObj = startDateObj + timedelta(hours=1)
            else:
                endDateObj = datetime.strptime(endDate+' '+startTime, '%m/%d/%Y %I:%M %p')
            
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

        # tags store eventID and topic now
        tags = {}
        tags['eventId'] = pe['eventId']
        if 'topic' in pe:
            tags['topic'] = pe['topic']

        if len(tags) != 0:
            entry['tags'] = tags

        # find geographical location
        # TODO: do it in re match and set some file to record special conditions
        if 'location' in pe:
            if ("Stage" in pe['location'] or "Studio" in pe['location']) and "Krannert Center" in pe['calendarName']:
                location = "Krannert Center for the Performing Arts"
            else:
                location = pe['location']
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
    

    # output to a json file
    with open(jsonF, 'w') as jsonFile:
        json.dump(xmltoMongoDB, jsonFile, indent='\t')

    
def parseEventXML(xml='eventsExample.txt', jsonF='eventsExample.json'):

    with open(xml, "r") as sample:
        content = sample.read()

    tree = ET.fromstring(content)

    XML2Json = []

        


    


if __name__ == "__main__":
    

    # url = "https://urldefense.proofpoint.com/v2/url?u=https-3A__calendars.illinois.edu_eventXML11_25.xml&d=DwMFAg&c=OCIEmEwdEq_aNlsP4fF3gFqSN-E3mlr2t9JcDdfOZag&r=zSYD-leOsEp1PCmcy2SID6ksFPDJQDoexqAdxiBTDbg&m=7Tr33Vua2nrTVscJbfsKxTqIcoCpz_rfczepxDwATno&s=q9iUrc2PUVrWN38PyfZBep2hw8BINvurvZHk09Xg-2U&e="
    url = "https://calendars.illinois.edu/eventXML11/33.xml"
    extractEventXMLandParse(url=url)
    # parseEventXML()
