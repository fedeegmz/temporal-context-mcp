from datetime import datetime

from dateutil import tz

from .models import TimePattern


class TimeUtils:
    """Utilities for handling time and temporal patterns"""

    @staticmethod
    def get_current_datetime(timezone: str = "local") -> datetime:
        """Gets the current date/time in the specified timezone"""
        if timezone == "local":
            return datetime.now(tz.tzlocal())
        return datetime.now(tz.gettz(timezone))

    @staticmethod
    def format_time_pattern_description(pattern: TimePattern) -> str:
        """Generates a readable description of the time pattern"""
        descriptions = []

        if pattern.days_of_week:
            days_map = {
                0: "Sun",
                1: "Mon",
                2: "Tue",
                3: "Wed",
                4: "Thu",
                5: "Fri",
                6: "Sat",
            }
            days = [days_map[d] for d in pattern.days_of_week]
            descriptions.append(f"Days: {', '.join(days)}")

        if pattern.hour_range:
            start, end = pattern.hour_range
            descriptions.append(f"Schedule: {start:02d}:00-{end:02d}:00")

        if pattern.hours:
            hours_str = ", ".join([f"{h:02d}:00" for h in pattern.hours])
            descriptions.append(f"Hours: {hours_str}")

        if pattern.cron_pattern:
            descriptions.append(f"Patrón: {pattern.cron_pattern}")

        return " | ".join(descriptions) if descriptions else "Siempre activo"
