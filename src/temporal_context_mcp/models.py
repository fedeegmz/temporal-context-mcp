from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ContextType(Enum):
    WORK_SCHEDULE = "work_schedule"
    MOOD_PATTERN = "mood_pattern"
    RESPONSE_STYLE = "response_style"
    AVAILABILITY = "availability"
    FOCUS_TIME = "focus_time"


class TimePattern(BaseModel):
    """Defines time patterns using cron-like format"""

    days_of_week: list[int] | None = Field(
        description="Days of the week (0=Sunday, 6=Saturday)",
        default=None,
    )
    hours: list[int] | None = Field(
        description="Specific hours",
        default=None,
    )
    hour_range: tuple[int, int] | None = Field(
        description="Hour range (e.g., 9-17 for work hours)",
        default=None,
    )
    specific_dates: list[str] | None = Field(
        description="Specific dates (ISO format)",
        default=None,
    )
    cron_pattern: str | None = Field(
        description="Custom cron pattern",
        default=None,
    )


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
