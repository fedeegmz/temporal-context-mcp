from temporal_context_mcp.context_management import RecommendationRepository
from temporal_context_mcp.context_management.application import (
    FindCurrentTemporalContext,
    FindTemporalContext,
)
from temporal_context_mcp.context_management.application.dto.temporal_context_result_dto import (
    TemporalContextResultDto,
)
from temporal_context_mcp.context_management.domain import (
    TemporalContextRepository,
)
from temporal_context_mcp.context_management.infrastructure.recommendation_repository import (
    RecommendationRepositoryImpl,
)
from temporal_context_mcp.context_management.infrastructure.temporal_context_repository_impl import (
    TemporalContextRepositoryImpl,
)
from temporal_context_mcp.shared import (
    TimePatternUtils,
)


class Controller:
    def __init__(self) -> None:
        self.__ctx_repository: TemporalContextRepository = (
            TemporalContextRepositoryImpl()
        )
        self.__recommendation_repository: RecommendationRepository = (
            RecommendationRepositoryImpl()
        )
        self.__find_temporal_context = FindTemporalContext(self.__ctx_repository)
        self.__find_current_temporal_context = FindCurrentTemporalContext(
            temporal_context_repository=self.__ctx_repository,
            find_temporal_context=self.__find_temporal_context,
        )

    def get_current_context(self) -> TemporalContextResultDto | None:
        return self.__find_current_temporal_context.execute()

    def list_contexts(
        self,
        *,
        context_type: str | None = None,
        actives: bool | None = None,
    ) -> str:
        contexts = self.__find_temporal_context.execute(
            context_type=context_type,
            actives=actives,
        )
        result_text = f"📋 **Temporal Contexts** ({len(contexts)} found)\n\n"

        for context in contexts:
            status = "🟢 Active" if context.active else "🔴 Inactive"
            pattern_desc = TimePatternUtils(context.time_pattern).generate_description()
            last_used = (
                context.last_used.strftime("%Y-%m-%d %H:%M")
                if context.last_used
                else "Never"
            )

            result_text += f"""**{context.name}** ({context.id})
        • Type: {context.context_type}
        • Status: {status}
        • Pattern: {pattern_desc}
        • Priority: {context.priority}
        • Last used: {last_used}
        • Data: {len(context.context_data)} settings

        """

        return result_text
