from pydantic import BaseModel, Field

from temporal_context_mcp.shared import ContextType, TimePattern


class SaveTemporalContextDto(BaseModel):
    id: str | None = Field(default=None, description="Temporal Context ID")
    name: str = Field(..., description="Temporal context name")
    context_type: ContextType = Field(
        default=ContextType.FOCUS_TIME,
        description="Temporal context type",
    )
    time_pattern: TimePattern = Field(..., description="Temporal context time_pattern")
    priority: int = Field(default=1, description="Priority")
