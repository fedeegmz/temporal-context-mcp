from datetime import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP

from temporal_context_mcp.recommendation_repository import RecommendationRepository

from .context_repository import ContextRepository
from .models import ContextType, TemporalContext, TimePattern
from .time_utils import TimeUtils

mcp = FastMCP("temporal-context-mcp")

context_repository = ContextRepository()


@mcp.tool()
def get_current_context(timezone: str = "local") -> str:
    """Gets the current temporal context and recommendations

    Args:
        timezone: Timezone (optional, default: local)
    """
    current_time = TimeUtils.get_current_datetime(timezone)

    active_contexts = context_repository.find(actives=True)
    recommendations = RecommendationRepository.get_context_recommendations(
        active_contexts,
    )

    # Mark contexts as used
    for context in active_contexts:
        context_repository.mark_one_as_used(context.id)

    result_text = f"""🕒 **Current Temporal Context** ({current_time.strftime("%Y-%m-%d %H:%M:%S")})

**Active Contexts:** {len(active_contexts)}
"""

    for context in active_contexts:
        pattern_desc = TimeUtils.format_time_pattern_description(
            context.time_pattern,
        )
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
        result_text += f"• Avoid topics: {', '.join(recommendations['avoid_topics'])}\n"

    return result_text


@mcp.tool()
def add_temporal_context(
    context_id: str,
    name: str,
    context_type: str,
    time_pattern: dict[str, Any],
    context_data: dict[str, Any],
    priority: int = 1,
) -> str:
    """Adds a new temporal context

    Args:
        context_id: Unique context ID
        name: Descriptive name
        context_type: Context type (work_schedule, mood_pattern, response_style, availability, focus_time)
        time_pattern: Time pattern configuration
        context_data: Context data (preferences, settings)
        priority: Priority (1=high, 3=low)
    """
    try:
        # Convert hour_range from list to tuple if it exists
        if "hour_range" in time_pattern:
            hour_range = time_pattern["hour_range"]
            if isinstance(hour_range, list) and len(hour_range) == 2:
                time_pattern["hour_range"] = tuple(hour_range)

        time_pattern_obj = TimePattern(**time_pattern)

        context = TemporalContext(
            id=context_id,
            name=name,
            context_type=ContextType(context_type),
            time_pattern=time_pattern_obj,
            context_data=context_data,
            priority=priority,
            created_at=datetime.now(),
        )

        success = context_repository.save(context)

        if success:
            pattern_desc = TimeUtils.format_time_pattern_description(time_pattern_obj)
            return f"✅ Context '{context.name}' successfully added.\nPattern: {pattern_desc}"
        return f"❌ Error: A context with ID '{id}' already exists"

    except Exception as e:
        return f"❌ Error creating context: {e!s}"


@mcp.tool()
def list_contexts(
    context_type: str | None = None,
    active_only: bool = False,
) -> str:
    """Lists all temporal contexts

    Args:
        context_type: Filter by context type (optional)
        active_only: Only currently active contexts
    """
    contexts = context_repository.find()

    if active_only:
        contexts = context_repository.find(context_type=context_type, actives=True)

    result_text = f"📋 **Temporal Contexts** ({len(contexts)} found)\n\n"

    for context in contexts:
        status = "🟢 Active" if context.active else "🔴 Inactive"
        pattern_desc = TimeUtils.format_time_pattern_description(
            context.time_pattern,
        )
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


@mcp.tool()
def update_context(context_id: str, updates: dict[str, Any]) -> str:
    """Updates an existing temporal context

    Args:
        context_id: ID of the context to update
        updates: Fields to update
    """
    success = context_repository.update_one_by_id(context_id, updates)

    if success:
        return f"✅ Context '{context_id}' successfully updated."
    return f"❌ Error: Context '{context_id}' not found"


@mcp.tool()
def delete_context(context_id: str) -> str:
    """Deletes a temporal context

    Args:
        context_id: ID of the context to delete
    """
    # Verify that the context exists before deleting
    context = context_repository.find_one_by_id(context_id)
    if not context:
        return f"❌ Error: Context '{context_id}' not found"

    success = context_repository.delete_one_by_id(context_id)

    if success:
        return f"✅ Context '{context.name}' ({context_id}) successfully deleted."
    return f"❌ Error deleting context '{context_id}'"


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
