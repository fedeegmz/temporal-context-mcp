from temporal_context_mcp.context_management.domain import (
    TemporalContext,
    TemporalContextRepository,
)
from temporal_context_mcp.shared import ContextType


class FindTemporalContext:
    def __init__(self, temporal_context_repository: TemporalContextRepository) -> None:
        self.temporal_context_repository = temporal_context_repository

    def execute(
        self,
        *,
        context_id: str | None = None,
        context_type: ContextType | None = None,
        actives: bool | None = None,
    ) -> list[TemporalContext]:
        if context_id is not None:
            context = self.temporal_context_repository.find_one_by_id(context_id)
            return [context] if context else []
        return self.temporal_context_repository.find(
            context_type=context_type,
            actives=actives,
        )
