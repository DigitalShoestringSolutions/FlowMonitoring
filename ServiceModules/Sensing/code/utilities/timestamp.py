# timestamp.py

# do we need to use both of these together?
import time
import datetime


def get_timestamp():
    """Get a string containing the current lcoal time in ISO8601 format"""
    __dt = -1 * (time.timezone if (time.localtime().tm_isdst == 0) else time.altzone)
    tz = datetime.timezone(datetime.timedelta(seconds=__dt))
    return datetime.datetime.now(tz=tz).isoformat()
