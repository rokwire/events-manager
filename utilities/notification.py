import requests
import traceback
from ..config import Config
from pyfcm import FCMNotification


push_service = FCMNotification(api_key=Config.FCM_SERVER_API_KEY)


def get_favorite_eventid_information(eventid):
    data = dict()
    url = "%s%s" % (Config.FAVORITE_EVENTID_ENDPOINT_PREFIX, eventid)
    headers = {"ROKWIRE-API-KEY": Config.ROKWIRE_API_KEY}
    req = requests.get(url, headers=headers)
    if req.status_code == 200:
        req_data = req.json()
        data['ndevices'] = len(req_data)
        data['tokens'] = [device.get("deviceToken") for device in req_data]
    return data


def send_notification(title, body, tokens):
    try:
        result = push_service.notify_multiple_devices(registration_ids=tokens, message_title=title, message_body=body)
        print(result)
    except Exception as ex:
        traceback.print_exc()

