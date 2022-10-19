#  Copyright 2022 Board of Trustees of the University of Illinois.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import ast
import json

from datetime import timedelta
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config(object):
    # MONGO_URL to setup connection with target mongoDB
    MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    # MONGO_DATABASE refers to the mongoDB's database that we are about to access to
    MONGO_DATABASE = os.getenv("MONGO_DATABASE", "rokwire")

    # URL prefix to the events manager
    URL_PREFIX = os.getenv("URL_PREFIX", "/events-manager")

    # It refers to database system we use. Currently it should be "mongoDB".
    DBTYPE = os.getenv("DBTYPE", 'mongoDB')

    # SECRET_KEY is used to signing session cookie
    SECRET_KEY = os.getenv("SECRET_KEY", "SECRET_KEY")

    # GOOGLE_KEY is used to access Google Geocoding service
    GOOGLE_KEY = os.getenv("GOOGLE_KEY", "...")
    # GOOGLE_MAP_VIEW_KEY is used to access Google Maps View service
    GOOGLE_MAP_VIEW_KEY = os.getenv("GOOGLE_MAP_VIEW_KEY", "...")

    # EVENT_COLLECTION defines the event collection name we are using to store events
    EVENT_COLLECTION = os.getenv("EVENT_COLLECTION", "eventsmanager_events")

    # URL prefix to get the information of a specific event id.
    FAVORITE_EVENTID_ENDPOINT_PREFIX = os.getenv("FAVORITE_EVENTID_ENDPOINT_PREFIX", 'http://localhost:9001/profiles/device-data?favorites.eventId=')
    # URL of notification
    NOTIFICATION_URL = os.getenv("NOTIFICATION_URL", '...')
    # EVENT_URL_* are here for formatting the webtools url that we crawl webtool events from
    EVENT_URL_PREFIX = os.getenv("EVENT_URL_PREFIX", 'https://xml.calendars.illinois.edu/eventXML15/')
    EVENT_URL_SUFFIX = os.getenv("EVENT_URL_SUFFIX", '.xml')

    # This a mapping between webtools calendars id to name
    INT2CAL = [{"6991": "Illinois App Master Calendar"}]

    # This is a mapping between different sources to different calendar mapping
    INT2SRC = {
        '0': ('WebTools', INT2CAL),
        '1': ('EMS', []),
    }

    # EVENT_BUILDING_BLOCK_URL defines the target URL that we submit parsed events to
    EVENT_BUILDING_BLOCK_URL = os.getenv("EVENT_BUILDING_BLOCK_URL", "http://localhost:9000/events")

    # CALENDAR_COLLECTION defines a collection location for storing webtool calendar metadata
    CALENDAR_COLLECTION = os.getenv("CALENDAR_COLLECTION", 'calendars')

    # WEBTOOL_IMAGE_LINK_* are used for composing the image url that is associated with an event
    WEBTOOL_IMAGE_LINK_PREFIX = os.getenv('WEBTOOL_IMAGE_LINK_PREFIX', 'https://calendars.illinois.edu/eventImage')
    WEBTOOL_IMAGE_LINK_SUFFIX = os.getenv('WEBTOOL_IMAGE_LINK_SUFFIX', 'large.png')

    # WEBTOOL_CALENDAR_LINK_PREFIX are used for linking the webtools catagories to their respective illinois calendar page
    WEBTOOL_CALENDAR_LINK_PREFIX = os.getenv('WEBTOOL_CALENDAR_LINK_PREFIX', 'https://calendars.illinois.edu/list/')

    # ROKWIRE_IMAGE_LINK_FORMAT defines a url format for Rokwire image access for the associated event
    ROKWIRE_IMAGE_LINK_FORMAT = os.getenv('ROKWIRE_IMAGE_LINK_FORMAT', 'http://localhost:9000/events/{}/images/{}')
    ROKWIRE_IMAGE_LINK_PREFIX = os.getenv('ROKWIRE_IMAGE_LINK_PREFIX', 'http://localhost:9000/events/image')

    # IMAGE_COLLECTION defines a collection location for storing image metadata
    IMAGE_COLLECTION = os.getenv("IMAGE_COLLECTION", 'images')

    # WEBTOOL_IMAGE_MOUNT_POINT defines a image location for temporarily storing downloaded image
    WEBTOOL_IMAGE_MOUNT_POINT = os.getenv("WEBTOOL_IMAGE_MOUNT_POINT", './images')

    # Following variables are needed for mapping the Amazon S3 bucket and folder prefix
    AWS_IMAGE_FOLDER_PREFIX = os.getenv("AWS_IMAGE_FOLDER_PREFIX", "events")
    BUCKET = os.getenv("AWS_S3_BUCKET", "rokwire-events-s3-images")

    # Authentication ID Token - Request to event building block
    AUTHENTICATION_TOKEN = os.getenv("AUTHENTICATION_TOKEN", "...")
    # ROKWIRE API KEY
    ROKWIRE_API_KEY = os.getenv("ROKWIRE_API_KEY", "...")
    # Notification Auth Token
    FCM_SERVER_API_KEY = os.getenv("FCM_SERVER_API_KEY", "...")

    # Pagination Variables
    PER_PAGE = int(os.getenv("PER_PAGE", 5))
    # All Pagination Variables Available
    EVENTS_PER_PAGE = ast.literal_eval(os.getenv('EVENTS_PER_PAGE', "[5, 10, 20]"))

    # LDAP_* are used in NCSA or UIUC LDAP system for authentication access
    LDAP_ON = os.getenv("LDAP_ON", "False") == "True"
    LDAP_HOSTNAME = os.getenv("LDAP_HOSTNAME", "")
    LDAP_GROUP = os.getenv("LDAP_GROUP", "")
    LDAP_BASE_DN = os.getenv("LDAP_BASE_DN", "")
    LDAP_USER_DN = os.getenv("LDAP_USER_DN", "")
    LDAP_GROUP_DN = os.getenv("LDAP_GROUP_DN", "")
    LDAP_OBJECTCLASS = os.getenv("LDAP_OBJECTCLASS", "")
    LDAP_TRUST_ALL_CERTIFICATES = os.getenv("LDAP_TRUST_ALL_CERTIFICATES", "")

    # ADMINS defines a list usernames that serve as administrators
    ADMINS = []

    # SCHEDULER_* defines hours and mins for scheduler to run on daily base crawling
    SCHEDULER_HOUR = os.getenv("SCHEDULER_HOUR", '')
    SCHEDULER_MINS = os.getenv("SCHEDULER_MINS", '')

    # OIDC CONFIG FOR LOGIN
    ISSUER_URL = os.getenv("ISSUER_URL", "https://shibboleth.illinois.edu")
    SCOPES = ast.literal_eval(os.getenv("SCOPES", '["openid", "profile", "email", "offline_access"]'))  # Other OIDC scopes can be added as needed.
    REDIRECT_URIS = os.getenv("REDIRECT_URIS", "")
    CLIENT_ID = os.getenv("CLIENT_ID", "")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")

    # LOGIN_MODE SELECTED
    LOGIN_MODE = os.getenv("LOGIN_MODE", "shibboleth")  # TODO: Add an option "local" for local login.

    # Role of users
    ROLE = {
       "both": (2, URL_PREFIX + "/"),
       "source": (1, URL_PREFIX + "/event/source/0"),
       "user": (1, URL_PREFIX + "/user-events"),
       "either": (0, None)
    }

    # SESSION EXPIRATION TIME
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.getenv("SESSION_LIFETIME_IN_HOURS", 1)))

    # Allowed image extensions for user event image upload
    ALLOWED_IMAGE_EXTENSIONS = ast.literal_eval(os.getenv('ALLOWED_IMAGE_EXTENSIONS', "{'png', 'jpg', 'jpeg', 'gif'}"))

    # The limit of user-uploaded image (measured in MB)
    IMAGE_SIZE_LIMIT = int(os.getenv('IMAGE_SIZE_LIMIT', 1))

    # Excluded location for calculating geo location
    EXCLUDED_LOCATION = ast.literal_eval(os.getenv("EXCLUDED_LOCATION", "{'zoom', 'online'}"))

    # Time zones for user to select from
    TIMEZONES = json.loads(os.getenv("TIMEZONES", '{"US/Pacific": "US/Pacific","US/Mountain": "US/Mountain", '
                                                  '"US/Central": "US/Central", "US/Eastern": "US/Eastern"}'))

    GROUPS_BUILDING_BLOCK_BASE_URL = os.getenv("GROUPS_BUILDING_BLOCK_BASE_URL", "https://api-dev.rokwire.illinois.edu/gr/api/")

    # API key used to communicate with groups building block
    INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")    # pragma: allowlist secret
