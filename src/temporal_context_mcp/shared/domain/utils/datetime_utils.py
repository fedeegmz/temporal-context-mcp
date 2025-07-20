from datetime import datetime

from dateutil import tz


def get_current_datetime(timezone: str = "local") -> datetime:
    """Gets the current date/time in the specified timezone"""
    if timezone == "local":
        return datetime.now(tz.tzlocal())
    return datetime.now(tz.gettz(timezone))
