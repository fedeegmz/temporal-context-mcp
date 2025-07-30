from pydantic import BaseModel, Field


class TimePattern(BaseModel):
    """Defines time patterns using a cron-like format"""

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
