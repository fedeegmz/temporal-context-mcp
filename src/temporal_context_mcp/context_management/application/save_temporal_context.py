from temporal_context_mcp.context_management.domain import (
    TemporalContext,
    TemporalContextRepository,
)
from temporal_context_mcp.context_management.infrastructure.dto import (
    SaveTemporalContextDto,
)
from temporal_context_mcp.shared import (
    Priority,
    generate_id,
    get_current_datetime,
)


class SaveTemporalContext:
    def __init__(self, temporal_context_repository: TemporalContextRepository) -> None:
        self.temporal_context_repository = temporal_context_repository

    def execute(self, *, dto: SaveTemporalContextDto) -> bool:
        temporal_context = TemporalContext(
            id=dto.id or generate_id(),
            name=dto.name,
            context_type=dto.context_type,
            time_pattern=dto.time_pattern,
            context_data=dto.context_data,
            priority=Priority(dto.priority),
            created_at=get_current_datetime(),
        )
        return self.temporal_context_repository.save(temporal_context)
