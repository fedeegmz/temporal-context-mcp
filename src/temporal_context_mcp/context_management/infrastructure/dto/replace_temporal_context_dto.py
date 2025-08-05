from typing import Any

from pydantic import BaseModel, Field

from temporal_context_mcp.shared import ContextType, TimePattern


class ReplaceTemporalContextDto(BaseModel):
    name: str | None = Field(default=None, description="Temporal context name")
    context_type: ContextType | None = Field(
        default=None,
        description="Temporal context type",
    )
    time_pattern: TimePattern | None = Field(
        default=None,
        description="Temporal context time_pattern",
    )
    context_data: dict[str, Any] | None = Field(
        default=None,
        description="Temporal context data",
    )
    priority: int | None = Field(default=None, description="Priority")
