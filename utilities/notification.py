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

import requests
import traceback
from ..config import Config
from pyfcm import FCMNotification
import logging
from time import gmtime
logging.Formatter.converter = gmtime
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%dT%H:%M:%S',
                    format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s [%(threadName)-10s] : %(name)s - %(message)s')
__logger = logging.getLogger("notification.py")


push_service = FCMNotification(api_key=Config.FCM_SERVER_API_KEY)


def get_favorite_eventid_information(eventId):
    data = dict()
    url = "%s%s" % (Config.FAVORITE_EVENTID_ENDPOINT_PREFIX, eventId)
    headers = {"ROKWIRE-API-KEY": Config.ROKWIRE_API_KEY}
    req = requests.get(url, headers=headers)
    if req.status_code == 200:
        req_data = req.json()
        data['ndevices'] = len(req_data)
        data['tokens'] = [device.get("deviceToken") for device in req_data]
    return data


def send_notification(title, body, data, tokens):
    try:
        result = push_service.notify_multiple_devices(registration_ids=tokens, message_title=title, message_body=body,
                                                      data_message=data)
        __logger.info(result)
    except Exception as ex:
        __logger.exception(ex)

