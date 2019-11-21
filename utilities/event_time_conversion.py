import pytz
from timezonefinder import TimezoneFinder


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
            print("Cannot find timezone for geolocation: latitude=%s, longitude=%s" % (latitude, longitude))
        else:
            local_tz = pytz.timezone(tz_name)
    datetime_with_tz = local_tz.localize(datetime_without_tz, is_dst=None)  # No daylight saving time
    datetime_in_utc = datetime_with_tz.astimezone(pytz.utc)
    return datetime_in_utc.strftime('%Y-%m-%dT%H:%M:%S')
