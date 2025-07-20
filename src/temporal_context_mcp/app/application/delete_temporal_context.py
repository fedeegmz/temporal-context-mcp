from temporal_context_mcp.app.domain.ports.temporal_context_repository import (
    TemporalContextRepository,
)


class DeleteTemporalContext:
    def __init__(self, temporal_context_repository: TemporalContextRepository) -> None:
        self.temporal_context_repository = temporal_context_repository

    def execute(self, *, context_id: str) -> bool:
        return self.temporal_context_repository.delete_one_by_id(
            context_id=context_id,
        )
