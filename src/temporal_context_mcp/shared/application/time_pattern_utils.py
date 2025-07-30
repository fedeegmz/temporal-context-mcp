from datetime import datetime

from croniter import croniter

from temporal_context_mcp.shared.domain.time_pattern import TimePattern

SECONDS_IN_MINUTE = 60


class TimePatternUtils:
    def __init__(self, pattern: TimePattern) -> None:
        self.pattern = pattern
        self.days_map = {
            0: "Sun",
            1: "Mon",
            2: "Tue",
            3: "Wed",
            4: "Thu",
            5: "Fri",
            6: "Sat",
        }

    def generate_description(self) -> str:
        """Generates a readable description of the time pattern"""
        descriptions = []

        if self.pattern.days_of_week:
            days = [self.days_map[d] for d in self.pattern.days_of_week]
            descriptions.append(f"Days: {', '.join(days)}")

        if self.pattern.hour_range:
            start, end = self.pattern.hour_range
            descriptions.append(f"Schedule: {start:02d}:00-{end:02d}:00")

        if self.pattern.hours:
            hours_str = ", ".join([f"{h:02d}:00" for h in self.pattern.hours])
            descriptions.append(f"Hours: {hours_str}")

        if self.pattern.cron_pattern:
            descriptions.append(f"Patrón: {self.pattern.cron_pattern}")

        return " | ".join(descriptions) if descriptions else "Siempre activo"

    def is_time_match(self, target_time: datetime) -> bool:
        """Verifies if a specific moment matches the time pattern"""

        # Check days of the week
        if self.pattern.days_of_week:
            # Python: 0=Monday, 6=Sunday; Convert to 0=Sunday
            weekday = (target_time.weekday() + 1) % 7
            if weekday not in self.pattern.days_of_week:
                return False

        # Check specific hours
        if self.pattern.hours:
            if target_time.hour not in self.pattern.hours:
                return False

        # Check hour range
        if self.pattern.hour_range:
            start_hour, end_hour = self.pattern.hour_range
            if not (start_hour <= target_time.hour <= end_hour):
                return False

        # Check specific dates
        if self.pattern.specific_dates:
            date_str = target_time.strftime("%Y-%m-%d")
            if date_str not in self.pattern.specific_dates:
                return False

        # Check cron pattern
        if self.pattern.cron_pattern:
            try:
                cron = croniter(self.pattern.cron_pattern, target_time)
                # If the next execution is exactly now, it matches
                next_run = cron.get_next(datetime)
                return abs((next_run - target_time).total_seconds()) < SECONDS_IN_MINUTE
            except Exception:
                return False

        return True
