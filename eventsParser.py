from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
import xml.etree.ElementTree as ET
import requests
import json
import os
import logging

# set up logger globally and in flask, it can be done using app.logging
if not os.path.exists('logs'):
        os.mkdir('logs')
    
# CAUTION: logging message will not write to log file if its level is lower than file handler level
#          also it does not print to console if its level is less than root level
file_handler = RotatingFileHandler('events.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
file_handler.setLevel(logging.ERROR)

xmlLogger = logging.getLogger('xmlParser')
xmlLogger.addHandler(file_handler)
xmlLogger.setLevel(logging.INFO)


def checkElement(name, xmlMap):
    if name in xmlMap:
        if xmlMap[name] is not None:
            return True
    return False


def extractEventXMLandParse(url=None, filename='eventsExample.txt'):

    if url is None:
        return None
        
    response = requests.get(url)

    # Response Code should be 200 (OK)
    if response.status_code != 200:
        return None
    

    # CAUTION: text involved decode, may need to consider it later. Content may be useful to
    # handle byte data like photo

    content = response.text

    content = content.replace("&gt;", ">").replace("&lt;", "<")

    try:
        tree = ET.fromstring(content)
    except:
        xmlLogger.error("Invalid XML data")
        return None
    
    XML2Json = []

    # extract all contents from publicEvents
    for publicEvent in tree:
        
        # check for publicEvent tag
        if publicEvent.tag != "publicEventWS":
            continue
        
        eventDetail = {}
        for elem in publicEvent:
            if elem.tag == "description":
                eventDetail[elem.tag] = ET.tostring(elem).decode('utf-8')
            else:
                eventDetail[elem.tag] = elem.text

        XML2Json.append(eventDetail)

    # modify datetime format in XML, change it from 'MM/DD/YYYY HH/MIN' to 'DD/MM/YYYY HH/MIN/SS'
    # if endtime is not defined, then 
    #   if endDate is the same day as startDate, endtime will be defaultly set to 1 hour later
    #   if different, endtime will be set to 1 day after starttime
    for pe in XML2Json:
        
        if checkElement("startDate", pe):
            startDate = pe['startDate']
        else:
            pe.pop('startDate')
            pe['start'] = None
        
        if checkElement("endDate", pe):
            endDate = pe['endDate']
        else:
            pe.pop('endDate')
            pe['end'] = None
        
        if checkElement("startTime", pe):
            startTime = pe['startTime']
        else:
            pe['start'] = None


        startDateObj = datetime.strptime(startDate+' '+startTime, '%m/%d/%Y %I:%M %p')
        if pe['endTime'] is None:
            if endDate == startDate:
                endDateObj = startDateObj + timedelta(hours=1)
            else:
                endDateObj = datetime.strptime(endDate+' '+startTime, '%m/%d/%Y %I:%M %p')
        else:
            endTime = pe['endTime']
            endDateObj = datetime.strptime(endDate+' '+endTime, '%m/%d/%Y %I:%M %p')

        pe.pop('startDate')
        pe.pop('endDate')
        pe.pop('startTime')
        pe.pop('endTime')

        pe['start'] = startDateObj.strftime("%d/%m/%Y %H:%M:%S")
        pe['end'] = endDateObj.strftime("%d/%m/%Y %H:%M:%S")


    
def parseEventXML(xml='eventsExample.txt', jsonF='eventsExample.json'):

    with open(xml, "r") as sample:
        content = sample.read()

    tree = ET.fromstring(content)

    XML2Json = []


    # output to a json file
    print(type(XML2Json[0]['description']))
    with open(jsonF, 'w') as jsonFile:
        json.dump(XML2Json, jsonFile, indent='\t')

        


    


if __name__ == "__main__":




    # url = "https://urldefense.proofpoint.com/v2/url?u=https-3A__calendars.illinois.edu_eventXML11_25.xml&d=DwMFAg&c=OCIEmEwdEq_aNlsP4fF3gFqSN-E3mlr2t9JcDdfOZag&r=zSYD-leOsEp1PCmcy2SID6ksFPDJQDoexqAdxiBTDbg&m=7Tr33Vua2nrTVscJbfsKxTqIcoCpz_rfczepxDwATno&s=q9iUrc2PUVrWN38PyfZBep2hw8BINvurvZHk09Xg-2U&e="
    url = "https://calendars.illinois.edu/eventXML11/25.xml"
    # extractEventXMLandSave(url)
    parseEventXML()
