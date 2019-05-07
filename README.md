# Command Line Parser Tool for XML Event Parsing

## Description

This parser converts XML content from target URLs to json format defined by [Rokwire YAML file](https://github.com/rokwire/rokwire-building-blocks-api/blob/develop/rokwire.yaml), the usage of the YAML file is explained [here](https://github.com/rokwire/rokwire-building-blocks-api)

The parsing is divided into two sections:
(elements in regular style are elements in parsed json content)
(elements in **bold style** are elements in raw XML content)
- Required Fields:
    - eventType: extracted from **eventType**
    - sponsor: extracted from **sponsor** 
    - title: extracted from **title**
    - startDate: extracted from **startDate** and **startTime** and convert them into *ISO-8601* format
    - endDate: **timeType** will provide information about whether **endTime** exists or not
        * if **endTime** does not exist, 
            - if **endDate** is the same as **startDate**, set endDate to be one hour later than the startDate above in *ISO-8601* format
            - if **endDate** is one or more days off, set endDate to be the same time as startDate above in *ISO-8601* format
        * if **endTime** exists, extracted from **endDate** and **endTime** and convert them into *ISO-8601* format
- Optional Fields:
    - description: extracted from **description** and furthered parsed by *Beautiful Soup 4.4* 
    - titleURL: extracted from **titleURL** 
    - speaker: extracted from **speaker** 
    - registrationURL: extracted from **registrationURL** 
    - cost: extracted from **cost**, it is likely to be String Type
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
        * **eventId** 
        * **topic.name** 
    - location: extracted from **location** 
        * location information provided by URL is usually not exact, there are two API service to solve it
            - [Google Geocoding API](https://cloud.google.com/maps-platform/), it has relatively accurate and complete database for lookup and it may has a fast response towards request but it is not tested yet. However, it requires a paid private account for accessing
            - [Nominatim](http://nominatim.org/), it is currently in use for this parser. It is free with unlimited access. 
                * The usage for Nominatim is quite straighforward, this parser use *https://nominatim.openstreetmap.org/search?q=location&format=json* with location found in XML
                * For more usage, [Documentation](http://nominatim.org/release-docs/latest/api/Overview/) is provided

## TO-DO List and Potential Issues:
- [] Insert logging utility for future debugging
- [] Insert Exception Catch unit
- [] Insert arguments handling for potential flask CLI usage
- [] Decides how to set endDate by default
- [] Decides which geolocation API we should use
- [] Figure out what does the number in ical and outlook download links refer to. For example, a sample event has ical download like: **"https://calendars.illinois.edu/ical/7/33338116.ics"**. Then, what does **7** means here. 
- [] Fix encoding issue. Some characters are encoded in unicode and parsed into ascii. It appears usually in **speaker**

## Results and Raw XML content

JSON file after parsing is [here](./eventsExample.json)
Original XML content is [here](./eventsExample.xml)