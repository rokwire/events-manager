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

import traceback
import requests

from flask import current_app

# this function is used for checking if event has large png image for displaying
# it returns true when it gets the image and store it in local folder, else it will       
# return false. There is one thing to notice is that the image name is composed of 
# dataSourceId(since we do not know about eventId in parsing)
def downloadImage(calendarId, dataSourceEventId, eventId, prefix_path=None):
    webtool_image_url = "{}/{}/{}/{}".format(
        current_app.config['WEBTOOL_IMAGE_LINK_PREFIX'],
        calendarId,
        dataSourceEventId,
        current_app.config['WEBTOOL_IMAGE_LINK_SUFFIX']
    )
    image_store_path = current_app.config['WEBTOOL_IMAGE_MOUNT_POINT']
    if prefix_path:
        image_store_path = prefix_path

    try:
        image_response = requests.get(webtool_image_url)
        if image_response.status_code == 200:
            with open('{}/{}.jpg'.format(image_store_path, eventId), 'wb') as image:
                for chunk in image_response.iter_content(chunk_size=128):
                    image.write(chunk)
            return True
    except Exception:
        traceback.print_exc()
        return False
    return False
