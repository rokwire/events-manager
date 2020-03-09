# This is used as customed geolocation for different calendar sources
CalName2Location = {
    'General Events': '',
    'Krannert Center': (40.1080244,-88.224704),
    'Library Calendar': '',
    'Facility Hours': '',
    'Beckman Main Calendar': (40.1157707,-88.229393),
    'Lincoln Hall Theater Events': (40.1066066,-88.2304212),
    'Foellinger Auditorium Events': (40.1059431,-88.2294751),
    'Department of Sociology': (40.1066528,-88.2305061),
    'NCSA': (40.1147743,-88.2252053),
}


# This is for confusing maps localization
# Usage is for enforce matching: [Name, Sponsor keyword, location keyword, accessName]
tip4CalALoc = [
    ['Krannert Center', '', 'studio', 'Krannert Center'],
    ['Krannert Center', '', 'stage', 'Krannert Center'],
    ['General Events', 'ncsa', 'ncsa', 'NCSA'],
    ['National Center for Supercomputing Applications master calendar', '', 'ncsa', 'NCSA']
]


# Mapping between webtool calendar event type to Rokwire categories
eventTypeMap = {
    "Exhibition":               "Entertainment",
    "Festival/Celebration":     "Entertainment",
    "Film Screening":           "Entertainment",
    "Performance":              "Entertainment",
    "Informational":            "Academic",
    "Lecture":                  "Academic",
    "Meeting":                  "Academic",
    "Reception/Open House":     "Academic",
    "Seminar/Symposium":        "Academic",
    "Ceremony/Service":         "Community",
    "Community Service":        "Community",
    "Social/Informal Event":    "Community",
    "Conference/Workshop":      "Career Development",
    "Professional Development": "Career Development",
    "Health/Fitness":           "Recreation",
    "Sporting Event":           "Athletics",
    "Sidearm":                  "Athletics",
    "Other":                    "Other",
}

# Rokwire Categories
# create dic for eventType values - new category
eventTypeValues = {}
for key in eventTypeMap:
    value = eventTypeMap[key]
    eventTypeValues[value] = 0
eventTypeValues = list(eventTypeValues.keys())

# Mapping between Rokwire event type and its subcategory(if the event type do have it)
subcategoriesMap = {
    "Athletics": [
        "Men's Basketball",
        "Women's Basketball",
        "Men's Cross Country",
        "Women's Cross Country",
        "Men's Golf",
        "Women's Golf",
        "Men's Gymnastics",
        "Women's Gymnastics",
        "Men's Tennis",
        "Women's Tennis",
        "Men's Track & Field",
        "Women's Track & Field",
        "Women's Soccer",
        "Baseball",
        "Football",
        "Softball",
        "Swim & Dive",
        "Wrestling",
        "Volleyball"
    ]
}

targetAudienceMap = ["Faculty/Staff", "Students", "Public", "Alumni", "Parents"]

#Geocoding list
predefined_locations = {
    "2700 Campus Way 45221":{
            'latitude': 39.131894,
            'longitude': -84.519143,
            'description': '2700 Campus Way 45221'
    },
    "Davenport 109A":{
            'latitude': 40.107335,
            'longitude': -88.226069,
            'description': 'Davenport Hall Room 109A'
    },
    "Nevada Dance Studio (905 W. Nevada St.)":{
            'latitude': 40.105825,
            'longitude': -88.219873,
            'description': 'Nevada Dance Studio, 905 W. Nevada St.'
    },
    "18th Ave Library, 175 W 18th Ave, Room 205, Oklahoma City, OK": {
        'latitude': 36.102183,
        'longitude': -97.111245,
        'description': '18th Ave Library, 175 W 18th Ave, Room 205, Oklahoma City, OK'
    },
    "Champaign County Fairgrounds": {
        'latitude': 40.1202191,
        'longitude': -88.2178757,
        'description': 'Champaign County Fairgrounds'
    },
    "Student Union SLC Conference room": {
        "latitude": 39.727282,
        "longitude": -89.617477,
        "description": "Student Union SLC Conference room"
    },
    "Student Union SLC Conference Room": {
        "latitude": 39.727282,
        "longitude": -89.617477,
        "description": "Student Union SLC Conference Room"
    },
    "Armory, room 172 (the Innovation Studio)":{
        'latitude': 40.104749,
        'longitude': -88.23195,
        'description': 'Armory, room 172 (the Innovation Studio)'
    },
    "Student Union Room 235": {
        'latitude': 39.727282,
        'longitude': -89.617477,
        'description': 'Student Union Room 235'
    },
    "Uni 206, 210, 211": {
        'latitude': 40.11314,
        'longitude': -88.225259,
        'description': 'Uni 206, 210, 211'
    },
    "Uni 205, 206, 210": {
        'latitude': 40.11314,
        'longitude': -88.225259,
        'description': 'Uni 205, 206, 210'
    },
    "Southern Historical Association Combs Chandler 30": {
        'latitude': 38.258116,
        'longitude': -85.756139,
        'description': 'Southern Historical Association Combs Chandler 30'
    },
    "St. Louis, MO": {
        'latitude': 38.694237,
        'longitude': -90.4493,
        'description': 'St. Louis, MO'
    },
    "Student Union SLC": {
        'latitude': 39.727282,
        'longitude': -89.617477,
        'description': 'Student Union SLC'
    },
    "Purdue University, West Lafayette, Indiana": {
        'latitude': 40.425012,
        'longitude': -86.912645,
        'description': 'Purdue University, West Lafayette, Indiana'
    },
    "MP 7": {
        'latitude': 40.100803,
        'longitude': -88.23604,
        'description': 'ARC MP 7'
    },
    "116 Roger Adams Lab": {
        'latitude': 40.107741,
        'longitude': -88.224943,
        'description': '116 Roger Adams Lab'
    },
}
