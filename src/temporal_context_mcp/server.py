from datetime import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP

from .models import ContextType, TemporalContext, TimePattern
from .temporal_store import TemporalStore
from .time_utils import TimeUtils

mcp = FastMCP("temporal-context-mcp")

# Initialize store
store = TemporalStore()


@mcp.tool()
def get_current_context(timezone: str = "local") -> str:
    """Gets the current temporal context and recommendations

    Args:
        timezone: Timezone (optional, default: local)
    """
    current_time = TimeUtils.get_current_datetime(timezone)

    active_contexts = TimeUtils.get_active_contexts(
        store.contexts,
        current_time,
    )
    recommendations = TimeUtils.get_context_recommendations(active_contexts)

    # Mark contexts as used
    for context in active_contexts:
        store.mark_context_used(context.id)

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
    id: str,
    name: str,
    context_type: str,
    time_pattern: dict[str, Any],
    context_data: dict[str, Any],
    priority: int = 1,
) -> str:
    """Adds a new temporal context

    Args:
        id: Unique context ID
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
            id=id,
            name=name,
            context_type=ContextType(context_type),
            time_pattern=time_pattern_obj,
            context_data=context_data,
            priority=priority,
            created_at=datetime.now(),
        )

        success = store.add_context(context)

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
    if context_type:
        contexts = store.list_contexts(ContextType(context_type))
    else:
        contexts = store.list_contexts()

    if active_only:
        current_time = TimeUtils.get_current_datetime()
        contexts = TimeUtils.get_active_contexts(contexts, current_time)

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
    success = store.update_context(context_id, updates)

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
    context = store.get_context(context_id)
    if not context:
        return f"❌ Error: Context '{context_id}' not found"

    success = store.delete_context(context_id)

    if success:
        return f"✅ Context '{context.name}' ({context_id}) successfully deleted."
    return f"❌ Error deleting context '{context_id}'"


@mcp.tool()
def preview_context(
    datetime_str: str | None = None,
    timezone: str = "local",
) -> str:
    """Previews which contexts would be active at a specific time

    Args:
        datetime_str: ISO datetime (optional, default: now)
        timezone: Timezone
    """
    if datetime_str:
        try:
            target_time = datetime.fromisoformat(datetime_str)
        except ValueError:
            return "❌ Error: Invalid date/time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
    else:
        target_time = TimeUtils.get_current_datetime(timezone)

    active_contexts = TimeUtils.get_active_contexts(
        store.contexts,
        target_time,
    )
    recommendations = TimeUtils.get_context_recommendations(active_contexts)

    result_text = f"""🔮 **Context Preview**
📅 Date/Time: {target_time.strftime("%Y-%m-%d %H:%M:%S")}
🌍 Timezone: {timezone}

**Contexts that would be active:** {len(active_contexts)}
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

    if not active_contexts:
        result_text += "\n• No active contexts at this time"
    else:
        result_text += f"""
**Recommendations that would apply:**
• Style: {recommendations["response_style"]}
• Formality: {recommendations["formality_level"]}
• Detail: {recommendations["detail_level"]}
• Urgent: {recommendations["time_sensitive"]}
"""

        if recommendations["suggested_tools"]:
            result_text += f"• Tools: {', '.join(recommendations['suggested_tools'])}\n"

        if recommendations["avoid_topics"]:
            result_text += f"• Avoid: {', '.join(recommendations['avoid_topics'])}\n"

    return result_text


if __name__ == "__main__":
    mcp.run(transport="stdio")
