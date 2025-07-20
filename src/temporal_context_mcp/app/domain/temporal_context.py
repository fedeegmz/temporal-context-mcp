from datetime import datetime
from typing import Any

from pydantic import BaseModel

from temporal_context_mcp.app.domain.context_type import ContextType
from temporal_context_mcp.app.domain.time_pattern import TimePattern


class TemporalContext(BaseModel):
    id: str
    name: str
    context_type: ContextType
    time_pattern: TimePattern
    context_data: dict[str, Any]
    active: bool = True
    created_at: datetime
    last_used: datetime | None = None
    priority: int = 1  # 1=high, 2=medium, 3=low
