from typing import Any

from temporal_context_mcp.app.domain.context_type import ContextType
from temporal_context_mcp.app.domain.ports.temporal_context_repository import (
    TemporalContextRepository,
)
from temporal_context_mcp.app.domain.temporal_context import TemporalContext
from temporal_context_mcp.app.domain.time_pattern import TimePattern
from temporal_context_mcp.shared.domain.utils.datetime_utils import get_current_datetime


class SaveTemporalContext:
    def __init__(self, temporal_context_repository: TemporalContextRepository) -> None:
        self.temporal_context_repository = temporal_context_repository

    def execute(
        self,
        *,
        context_id: str,
        name: str,
        context_type: str,
        time_pattern: dict[str, Any],
        context_data: dict[str, Any],
        priority: int = 1,
    ) -> bool:
        temporal_context = TemporalContext(
            id=context_id,
            name=name,
            context_type=ContextType(context_type),
            time_pattern=TimePattern(**time_pattern),
            context_data=context_data,
            priority=priority,
            created_at=get_current_datetime(),
        )
        return self.temporal_context_repository.save(temporal_context)
