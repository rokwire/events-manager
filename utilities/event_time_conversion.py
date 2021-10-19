#  Copyright 2020 Board of Trustees of the University of Illinois.
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

import pytz
from timezonefinder import TimezoneFinder
import logging
from time import gmtime
logging.Formatter.converter = gmtime
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%dT%H:%M:%S',
                    format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s [%(threadName)-10s] : %(name)s - %(message)s')
__logger = logging.getLogger("event_time_conversion.py")


def get_timezone_by_geolocation(latitude, longitude):
    tf = TimezoneFinder()
    return tf.timezone_at(lng=longitude, lat=latitude)


def utctime(datetime_without_tz, latitude, longitude):
    tz_name = None
    if latitude is None or longitude is None:
        # FIXME: if geolocation not provided, then use "US/Central" timezone.
        local_tz = pytz.timezone("US/Central")
    else:
        tz_name = get_timezone_by_geolocation(latitude, longitude)
        if not tz_name:
            # FIXME need extra service to get timezone for this geolocation
            local_tz = pytz.timezone("US/Central")
            __logger.info("Cannot find timezone for geolocation: latitude=%s, longitude=%s" % (latitude, longitude))
        else:
            local_tz = pytz.timezone(tz_name)
    datetime_with_tz = local_tz.localize(datetime_without_tz, is_dst=None)  # No daylight saving time
    datetime_in_utc = datetime_with_tz.astimezone(pytz.utc)
    return datetime_in_utc.strftime('%Y-%m-%dT%H:%M:%S')
