from temporal_context_mcp.context_management import (
    RecommendationRepository,
    TemporalContextRepository,
)
from temporal_context_mcp.context_management.application.dto import (
    TemporalContextResultDto,
)
from temporal_context_mcp.context_management.application.find_temporal_context import (
    FindTemporalContext,
)


class FindCurrentTemporalContext:
    def __init__(
        self,
        temporal_context_repository: TemporalContextRepository,
        recommendation_repository: RecommendationRepository,
        find_temporal_context: FindTemporalContext,
    ) -> None:
        self.__ctx_repository = temporal_context_repository
        self.__recommendation_repository = recommendation_repository
        self.__find_temporal_context = find_temporal_context

    def execute(self) -> TemporalContextResultDto | None:
        active_contexts = self.__find_temporal_context.execute(actives=True)
        sorted_contexts = sorted(active_contexts, key=lambda x: x.priority)
        if len(sorted_contexts) == 0:
            return None

        first_active_context = sorted_contexts[0]
        recommendation = self.__recommendation_repository.find_by_context_type(
            first_active_context.context_type,
        )
        self.__ctx_repository.mark_one_as_used(first_active_context.id)
        return TemporalContextResultDto(
            recommendation=recommendation,
            **first_active_context.model_dump(),
        )
