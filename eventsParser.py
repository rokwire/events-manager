from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from logging.handlers import RotatingFileHandler
from constants import CalName2Location, int2CalDB
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
            
            entry['startDate'] = startDateObj.strftime('%Y/%m/%dT%H:%M:%S')
            entry['endDate'] = endDateObj.strftime('%Y/%m/%dT%H:%M:%S')

        if pe['timeType'] == "ALL_DAY":
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
            location = pe['location']+', Urbana'

            QueryUrl = "{}{}".format(GeoUrl, urlencode({'q': location, 'format': 'json'}))
            GeoResponse = requests.get(QueryUrl)

            if GeoResponse.status_code != 200:
                xmlLogger.error("Invalid GeoURL Link", extra={'url': url, 'eventid': pe['eventid']})
            
            GeoContent = json.loads(GeoResponse.text)
            if len(GeoContent) != 0:
                lat = float(GeoContent[0]['lat'])
                lon = float(GeoContent[0]['lon'])
                # for now, since app is applied to Urbana, Champaign range, latitude and longitude are ranged
                if lat < 42 and lat > 40 and lon < -87 and lon > -89:
                    GeoInfo = {}
                    GeoInfo['latitude'] = lat
                    GeoInfo['longitude'] = lon
                    GeoInfo['description'] = GeoContent[0]['display_name']
                    GeoInfo['rawDescription'] = pe['location']
                    entry['location'] = GeoInfo
                else:
                    entry['location'] = {'rawDescription': pe['location']}
            # when it does not show any result, refer to its default location
            else:
                QueryUrl2="{}{}".format(GeoUrl, urlencode({'q': CalName2Location[pe['calendarName']], 'format': 'json'}))
                GeoResponse2 = requests.get(QueryUrl2)
                if GeoResponse2.status_code != 200:
                    xmlLogger.error("Invalid GeoURL Link", extra={'url': url, 'eventid': pe['eventid']})
                GeoContent2 = json.loads(GeoResponse2.text)
                if len(GeoContent2) != 0:
                    GeoInfo = {}
                    GeoInfo['latitude'] = float(GeoContent2[0]['lat'])
                    GeoInfo['longitude'] = float(GeoContent2[0]['lon'])
                    GeoInfo['description'] = GeoContent2[0]['display_name']
                    GeoInfo['rawDescription'] = pe['location']
                    entry['location'] = GeoInfo
                else:
                    entry['location'] = {'rawDescription': pe['location']}

        xmltoMongoDB.append(entry)
    
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
        print("Usage: python eventsParser.py -g|-e urls_file store_file|json_file")
        print("       -g: get raw XML contents")
        print("       urls_file: file that contains events urls separated by newline")
        print("       store_file: file that stores raw material")
        print("       -e: extract events information from urls")
        print("       urls_file: file that contains events urls separated by newline")
        print("       json_file: json file that stores parsed results")
        exit()

    option = sys.argv[1]
    if option == '-e':
        urls_file = sys.argv[2]
        json_file = sys.argv[3]
        parseResult = []
        with open(urls_file, "r") as urlsList:
            urls = urlsList.read().split("\n")

        for url in urls:
            parseResult = parseResult + extractEventXMLandParse(parseResult, url=url, jsonF=json_file)
        
        with open(json_file, 'w') as parseContainer:
            json.dump(parseResult, parseContainer, indent='\t')

    elif option == '-g':

        urls_file = sys.argv[2]
        store_file = sys.argv[3]

        with open(urls_file, "r") as urlsList:
            urls = urlsList.read().split("\n")
        
        with open(store_file, "w") as storeFile:
            pass
        
        for url in urls:
            accessEventXML(store_file, url)