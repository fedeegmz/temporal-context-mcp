from temporal_context_mcp.context_management.application import (
    DeleteTemporalContext,
    FindTemporalContext,
    SaveTemporalContext,
)
from temporal_context_mcp.context_management.domain import (
    TemporalContextRepository,
)
from temporal_context_mcp.context_management.infrastructure.recommendation_repository import (
    RecommendationRepository,
)
from temporal_context_mcp.context_management.infrastructure.temporal_context_repository_impl import (
    TemporalContextRepositoryImpl,
)
from temporal_context_mcp.shared import (
    TimePatternUtils,
    get_current_datetime,
)


class Controller:
    def __init__(self) -> None:
        self.__ctx_repository: TemporalContextRepository = (
            TemporalContextRepositoryImpl()
        )
        self.__recommendation_repository = RecommendationRepository()
        self.save_temporal_context = SaveTemporalContext(self.__ctx_repository)
        self.find_temporal_context = FindTemporalContext(self.__ctx_repository)
        self.delete_temporal_context = DeleteTemporalContext(self.__ctx_repository)

    def get_current_context(self, *, timezone: str = "local") -> str:
        formated_current_time = get_current_datetime(timezone).strftime(
            "%Y-%m-%d %H:%M:%S",
        )

        active_contexts = self.find_temporal_context.execute(actives=True)
        sorted_contexts = sorted(active_contexts, key=lambda x: x.priority)
        recommendation: dict[str, str] | None = None
        if len(sorted_contexts) > 0:
            recommendation = self.__recommendation_repository.find_by_context_type(
                sorted_contexts[0].context_type,
            )

        for context in active_contexts:
            self.__ctx_repository.mark_one_as_used(context.id)

        result_text = f"""🕒 **Current Temporal Context** ({formated_current_time})

        **Active Contexts:** {len(active_contexts)}
        """

        for context in active_contexts:
            pattern_desc = TimePatternUtils(context.time_pattern).generate_description()
            result_text += f"""
        • **{context.name}** ({context.context_type})
          - Pattern: {pattern_desc}
          - Priority: {context.priority}
        """

        result_text += f"""
        **Recommendations:**
        • Response style: {recommendation["response_style"]}
        • Formality level: {recommendation["formality_level"]}
        • Detail level: {recommendation["detail_level"]}
        • Time sensitive: {recommendation["time_sensitive"]}
        """

        if recommendation["suggested_tools"]:
            result_text += (
                f"• Suggested tools: {', '.join(recommendation['suggested_tools'])}\n"
            )

        if recommendation["avoid_topics"]:
            result_text += (
                f"• Avoid topics: {', '.join(recommendation['avoid_topics'])}\n"
            )

        return result_text

    def list_contexts(
        self,
        *,
        context_type: str | None = None,
        actives: bool | None = None,
    ) -> str:
        contexts = self.find_temporal_context.execute(
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
