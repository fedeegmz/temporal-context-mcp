from typing import Any

from temporal_context_mcp.context_management import (
    DeleteTemporalContext,
    FindTemporalContext,
    RecommendationRepository,
    RecommendationRepositoryImpl,
    SaveTemporalContext,
    TemporalContextRepository,
    TemporalContextRepositoryImpl,
)
from temporal_context_mcp.shared import (
    Priority,
    TimePattern,
    TimePatternUtils,
    get_current_datetime,
)


class Controller:
    def __init__(self) -> None:
        self.__ctx_repository: TemporalContextRepository = (
            TemporalContextRepositoryImpl()
        )
        self.__recommendation_repository: RecommendationRepository = (
            RecommendationRepositoryImpl()
        )
        self.save_temporal_context = SaveTemporalContext(self.__ctx_repository)
        self.find_temporal_context = FindTemporalContext(self.__ctx_repository)
        self.delete_temporal_context = DeleteTemporalContext(self.__ctx_repository)

    def get_current_context(self, *, timezone: str = "local") -> str:
        formated_current_time = get_current_datetime(timezone).strftime(
            "%Y-%m-%d %H:%M:%S",
        )

        active_contexts = self.find_temporal_context.execute(actives=True)
        recommendations = self.__recommendation_repository.get_context_recommendations(
            active_contexts,
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
        • Response style: {recommendations["response_style"]}
        • Formality level: {recommendations["formality_level"]}
        • Detail level: {recommendations["detail_level"]}
        • Time sensitive: {recommendations["time_sensitive"]}
        """

        if recommendations["suggested_tools"]:
            result_text += (
                f"• Suggested tools: {', '.join(recommendations['suggested_tools'])}\n"
            )

        if recommendations["avoid_topics"]:
            result_text += (
                f"• Avoid topics: {', '.join(recommendations['avoid_topics'])}\n"
            )

        return result_text

    def add_temporal_context(
        self,
        *,
        context_id: str,
        name: str,
        context_type: str,
        time_pattern: dict[str, Any],
        context_data: dict[str, Any],
        priority: int = 1,
    ) -> str:
        success = self.save_temporal_context.execute(
            context_id=context_id,
            name=name,
            context_type=context_type,
            time_pattern=time_pattern,
            context_data=context_data,
            priority=Priority(priority),
        )

        if success:
            pattern_desc = TimePatternUtils(
                TimePattern(**time_pattern),
            ).generate_description()
            return f"✅ Context '{name}' successfully added.\nPattern: {pattern_desc}"
        return f"❌ Error: A context with ID '{context_id}' already exists"

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

    def replace_context(
        self,
        *,
        context_id: str,
        name: str,
        context_type: str,
        time_pattern: dict[str, Any],
        context_data: dict[str, Any],
        priority: int = 1,
    ) -> str:
        success = self.save_temporal_context.execute(
            context_id=context_id,
            name=name,
            context_type=context_type,
            time_pattern=time_pattern,
            context_data=context_data,
            priority=Priority(priority),
        )

        if success:
            return f"✅ Context '{context_id}' successfully updated."
        return f"❌ Error: Context '{context_id}' not found"

    def delete_context(self, *, context_id: str) -> str:
        success = self.delete_temporal_context.execute(context_id=context_id)

        if success:
            return f"✅ Context ({context_id}) successfully deleted."
        return f"❌ Error deleting context '{context_id}'"
