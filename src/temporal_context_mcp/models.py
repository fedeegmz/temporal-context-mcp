from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class ContextType(Enum):
    WORK_SCHEDULE = "work_schedule"
    MOOD_PATTERN = "mood_pattern"
    RESPONSE_STYLE = "response_style"
    AVAILABILITY = "availability"
    FOCUS_TIME = "focus_time"


class TimePattern(BaseModel):
    """Defines time patterns using cron-like format"""

    # Days of the week (0=Sunday, 6=Saturday)
    days_of_week: list[int] | None = None
    # Specific hours
    hours: list[int] | None = None
    # Hour range (e.g., 9-17 for work hours)
    hour_range: tuple[int, int] | None = None
    # Specific dates
    specific_dates: list[str] | None = None  # ISO format
    # Custom cron pattern
    cron_pattern: str | None = None


class TemporalContext(BaseModel):
    """Context that applies at specific times"""

    id: str
    name: str
    context_type: ContextType
    time_pattern: TimePattern
    context_data: dict[str, Any]
    active: bool = True
    created_at: datetime
    last_used: datetime | None = None
    priority: int = 1  # 1=high, 2=medium, 3=low


class ContextResponse(BaseModel):
    """Response with applied context"""

    current_contexts: list[TemporalContext]
    recommendations: dict[str, Any]
    timestamp: datetime
