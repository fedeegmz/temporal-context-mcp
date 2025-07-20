from datetime import datetime

import croniter

from temporal_context_mcp.app.domain.time_pattern import TimePattern


def matches_time_pattern(pattern: TimePattern, target_time: datetime) -> bool:
    """Verifies if a specific moment matches the time pattern"""

    # Check days of the week
    if pattern.days_of_week:
        # Python: 0=Monday, 6=Sunday; Convert to 0=Sunday
        weekday = (target_time.weekday() + 1) % 7
        if weekday not in pattern.days_of_week:
            return False

    # Check specific hours
    if pattern.hours:
        if target_time.hour not in pattern.hours:
            return False

    # Check hour range
    if pattern.hour_range:
        start_hour, end_hour = pattern.hour_range
        if not (start_hour <= target_time.hour <= end_hour):
            return False

    # Check specific dates
    if pattern.specific_dates:
        date_str = target_time.strftime("%Y-%m-%d")
        if date_str not in pattern.specific_dates:
            return False

    # Check cron pattern
    if pattern.cron_pattern:
        try:
            cron = croniter.croniter(pattern.cron_pattern, target_time)
            # If the next execution is exactly now, it matches
            next_run = cron.get_next(datetime)
            return abs((next_run - target_time).total_seconds()) < 60
        except Exception:
            return False

    return True
