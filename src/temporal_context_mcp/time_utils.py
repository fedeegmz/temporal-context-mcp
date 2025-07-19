from datetime import datetime

import croniter
from dateutil import tz

from .models import TemporalContext, TimePattern


class TimeUtils:
    """Utilities for handling time and temporal patterns"""

    @staticmethod
    def get_current_datetime(timezone: str = "local") -> datetime:
        """Gets the current date/time in the specified timezone"""
        if timezone == "local":
            return datetime.now(tz.tzlocal())
        return datetime.now(tz.gettz(timezone))

    @staticmethod
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

    @staticmethod
    def get_active_contexts(
        contexts: list[TemporalContext],
        target_time: datetime | None = None,
    ) -> list[TemporalContext]:
        """Gets the active contexts for a specific moment"""
        if target_time is None:
            target_time = TimeUtils.get_current_datetime()

        active_contexts = [
            context
            for context in contexts
            if context.active
            and TimeUtils.matches_time_pattern(context.time_pattern, target_time)
        ]

        # Sort by priority
        active_contexts.sort(key=lambda x: x.priority)
        return active_contexts

    @staticmethod
    def get_context_recommendations(active_contexts: list[TemporalContext]) -> dict:
        """Generates recommendations based on active contexts"""
        recommendations = {
            "response_style": "normal",
            "formality_level": "medium",
            "detail_level": "medium",
            "suggested_tools": [],
            "avoid_topics": [],
            "time_sensitive": False,
        }

        for context in active_contexts:
            context_data = context.context_data

            if context.context_type == "work_schedule":
                recommendations.update(
                    {
                        "response_style": "professional",
                        "formality_level": "high",
                        "suggested_tools": ["calendar", "task_manager", "email"],
                        "time_sensitive": True,
                    },
                )

            elif context.context_type == "focus_time":
                recommendations.update(
                    {
                        "response_style": "concise",
                        "detail_level": "low",
                        "avoid_topics": ["entertainment", "social_media"],
                        "time_sensitive": True,
                    },
                )

            elif context.context_type == "mood_pattern":
                mood = context_data.get("mood", "neutral")
                if mood == "creative":
                    recommendations.update(
                        {
                            "response_style": "inspiring",
                            "suggested_tools": ["brainstorm", "ideation", "research"],
                        },
                    )
                elif mood == "tired":
                    recommendations.update(
                        {"response_style": "gentle", "detail_level": "low"},
                    )

            # Apply specific context configurations
            if "preferences" in context_data:
                recommendations.update(context_data["preferences"])

        return recommendations

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
