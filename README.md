# Command Line Parser Tool for XML Event Parsing for School XML calendar

## Usage
python -g|-e eventsParser.py url_file store_file|json_file<br/>
&nbsp;&nbsp;&nbsp;&nbsp;-g: get raw material from urls<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;url_file: it contains list of urls separated by line for events extraction<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;store_file: it stores raw xml content<br />
&nbsp;&nbsp;&nbsp;&nbsp;-e: parse raw xml material into json content from urls<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;url_file: it contains list of urls separated by line for events extraction<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;json_file: json file that stores parsed result
&nbsp;&nbsp;&nbsp;&nbsp;-f: parse raw xml material into json content from events xml file<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;xml_file: it contains raw xml contents for events extraction<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;json_file: json file that stores parsed result


## Description

This parser converts XML content from target URLs to json format defined by [Rokwire YAML file](https://github.com/rokwire/rokwire-building-blocks-api/blob/develop/rokwire.yaml), the usage of the YAML file is explained [here](https://github.com/rokwire/rokwire-building-blocks-api)

The parsing is divided into two sections:<br />
(elements in regular style are elements in parsed json content)<br />
(elements in **bold style** are elements in raw XML content)<br />
(time elements are output in format YY/MM/DDTHH:mm:ss)
- Required Fields:
    - eventType: extracted from **eventType**
    - sponsor: extracted from **sponsor** 
    - title: extracted from **title**
    - allDay: default set to False. When **timeType** is ALL_DAY, it is set to True
    - source: extracted from **calendarId**
    - startDate: **timeType** will provide information about whether **startTime** exists or not
        * if **timeType** is **ALL_TIME**, 
            - startDate is set to 00:00 in the **startDate**
        * else extracted from **startDate** and **startTime**
    - endDate: **timeType** will provide information about whether **endTime** exists or not
        * if **timeType** is **START_TIME_ONLY** or **ALL_TIME**, 
            - endDate is set to 23:59 in the **endDate**
        * else extracted from **endDate** and **endTime**
    - eventStauts: now defaulted to incomplete but from reliable sources, it should be marked as approved
- Optional Fields:
    - description: extracted from **description** and furthered parsed by *Beautiful Soup 4.4* 
    - titleURL: extracted from **titleURL** 
    - speaker: extracted from **speaker** 
    - registrationURL: extracted from **registrationURL** 
    - cost: extracted from **cost**, it is likely to be String Type
    - icalUrl: composed ical file url from **calendarId** and **eventId**
    - outlookUrl: composed outlook 2010 file url from **calendarId** and **eventId**
    - targetAudience: extracted from
        * **audienceFacultyStaff**
        * **audienceStudents**
        * **audiencePublic**
        * **audienceAlumni**
        * **audienceParents**
    - contacts: extracted from 
        * **contactName**
            - firstName and lastName are accessed by splitting the **contactName**
        * **contactEmail**
        * **contactPhone** 
    - tags: extracted from 
        * **topic.name** 
    - location: extracted from **location** 
        * location information provided by URL is usually not exact, there are two API service to solve it
            - [Google Geocoding API](https://cloud.google.com/maps-platform/), it has relatively accurate and complete database for lookup and it may has a fast response towards request but it is not tested yet. However, it requires a paid private account for accessing
            - The usage for API is through googlmap module which is completed by Google. The Documentation is 
              [here](https://googlemaps.github.io/google-maps-services-python/docs/)
            - It is proven that google API provides more comprehensive results by location inputs
            - For the current process, initially, location will be used to do hardcode matching because some descriptions are confusing. If there are no match, it will be searched through API and extract out the corresponding information. 
            - For simplicity, pick the first one of the results.
            - [Nominatim](http://nominatim.org/), it is currently in use for this parser. It is free with unlimited access. 
                * The usage for Nominatim is quite straighforward, this parser use *https://nominatim.openstreetmap.org/search?q=location&format=json* with location found in XML
                * There are multiple results appeared usually. For simplicity, it picks the first result
                * For more usage, [Documentation](http://nominatim.org/release-docs/latest/api/Overview/) is provided

## Logging and Exception:

(The logging format is: **asctime levelname: message -URL:'url'-EventID: eventid**)<br />

Exception has been placed on: 
- Error accessing XML url
- Error analyzing XML data
- Error finding distinguished tags from *publicEventWS*
- Error parsing html content from *description*
- Error accesing geographical API

Logging has been placed on:
- Record the amount of received events
- Record event that is under parsing
- Record the amount of parsed events


## TO-DO List and Potential Issues:
- [x] Insert logging utility for future debugging
- [x] Insert Exception Catch unit
- [x] Insert arguments handling for potential flask CLI usage
- [x] Decides how to set endDate by default
- [x] Decides which geolocation API we should use
- [x] Figure out what does the number in ical and outlook download links refer to. For example, a sample event has ical download like: **"https://calendars.illinois.edu/ical/7/33338116.ics"**. Then, what does **7** means here. (The answer is that the number refers to events location. For example, 33 means Krannert Center)
- [x] Fix encoding issue. Some characters are encoded in unicode and parsed into ascii. It appears usually in **speaker**

## Results and Raw XML content

JSON file after parsing is [here](./display.json)<br />
Original XML content is [here](./display.xml)
