from datetime import datetime

from pydantic import BaseModel

from temporal_context_mcp.shared import ContextType, Priority, TimePattern


class TemporalContext(BaseModel):
    id: str
    name: str
    context_type: ContextType
    time_pattern: TimePattern
    active: bool = True
    created_at: datetime
    last_used: datetime | None = None
    priority: Priority = Priority.LOW
