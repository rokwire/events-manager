import pytz


def utctime(datetime_without_tz):
    # FIXME: temporarily use US/Central for webtool events
    local_tz = pytz.timezone("US/Central")
    datetime_with_tz = local_tz.localize(datetime_without_tz, is_dst=None)  # No daylight saving time
    datetime_in_utc = datetime_with_tz.astimezone(pytz.utc)
    return datetime_in_utc.strftime('%Y-%m-%dT%H:%M:%S')
