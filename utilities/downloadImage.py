import traceback
import requests

from flask import current_app

# this function is used for checking if event has large png image for displaying
# it returns true when it gets the image and store it in local folder, else it will       
# return false. There is one thing to notice is that the image name is composed of 
# dataSourceId(since we do not know about eventId in parsing)
def downloadImage(calendarId, dataSourceEventId, eventId):
    webtool_image_url = "{}/{}/{}/{}".format(
        current_app.config['WEBTOOL_IMAGE_LINK_PREFIX'],
        calendarId,
        dataSourceEventId,
        current_app.config['WEBTOOL_IMAGE_LINK_SUFFIX']
    )

    try:
        image_response = requests.get(webtool_image_url)
        if image_response.status_code == 200:
            with open('{}/{}.png'.format(current_app.config['WEBTOOL_IMAGE_MOUNT_POINT'], eventId), 'wb') as image:
                for chunk in image_response.iter_content(chunk_size=128):
                    image.write(chunk)
            return True
    except Exception:
        traceback.print_exc()
        return False
    return False