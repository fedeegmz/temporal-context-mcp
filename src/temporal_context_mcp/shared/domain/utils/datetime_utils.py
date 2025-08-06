from datetime import datetime

from dateutil import tz


def get_current_datetime() -> datetime:
    """Gets the current date/time in the specified timezone"""
    return datetime.now(tz.tzlocal())
