int2CalDB = 
    {'7': "General Events"},
    {'33': "Krannert Center"},
    {'47': 'Library Calendar'},
    {'63': 'Facility Hours'},
    {'117': 'Beckman Main Calendar'},
    {'127': "Lincoln Hall Theater Events"},
    {'128': 'Foellinger Auditorium Events'},
    {'169': 'Department of Sociology'},
]

int2SrcDB= {
    '0': ('WebTools', int2CalDB),
    '1': ('EMS', ),
}

CalName2Location = {
    'General Events': '',
    'Krannert Center': (40.1080244,-88.224704),
    'Library Calendar': '',
    'Facility Hours': '',
    'Beckman Main Calendar': (40.1157707,-88.229393),
    'Lincoln Hall Theater Events': (40.1066066,-88.2304212),
    'Foellinger Auditorium Events': (40.1059431,-88.2294751),
    'Department of Sociology': (40.1066528,-88.2305061),
    'NCSA': (40.9951304,-89.0669566),
}

# This is for confusing maps localization
# Usage is for enforce matching: [Name, Sponsor keyword, location keyword, accessName]
tip4CalALoc = [
    ['Krannert Center', '', 'studio', 'Krannert Center'],
    ['Krannert Center', '', 'stage', 'Krannert Center'],
    ['General Events', 'ncsa', 'ncsa', 'NCSA'],
]
