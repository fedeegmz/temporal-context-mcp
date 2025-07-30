from typing import Any

from mcp.server.fastmcp import FastMCP

from temporal_context_mcp.context_management import (
    Controller,
    TemporalContextRepository,
    TemporalContextRepositoryImpl,
)

mcp = FastMCP("temporal-context-mcp")

context_repository: TemporalContextRepository = TemporalContextRepositoryImpl()
controller = Controller()


@mcp.tool()
def get_current_context(timezone: str = "local") -> str:
    """Gets the current temporal context and recommendations

    Args:
        timezone: Timezone (optional, default: local)
    """
    return controller.get_current_context(timezone=timezone)


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
        return controller.add_temporal_context(
            context_id=context_id,
            name=name,
            context_type=context_type,
            time_pattern=time_pattern,
            context_data=context_data,
            priority=priority,
        )
    except Exception as e:
        return f"❌ Error creating context: {e!s}"


@mcp.tool()
def list_contexts(
    context_type: str | None = None,
    actives: bool | None = None,
) -> str:
    """Lists all temporal contexts

    Args:
        context_type: Filter by context type (optional)
        actives: Filter currently active/inactive contexts
    """
    return controller.list_contexts(
        context_type=context_type,
        actives=actives,
    )


@mcp.tool()
def replace_context(
    context_id: str,
    name: str,
    context_type: str,
    time_pattern: dict[str, Any],
    context_data: dict[str, Any],
    priority: int = 1,
) -> str:
    """Updates an existing temporal context

    Args:
        context_id: Unique context ID
        name: Descriptive name
        context_type: Context type (work_schedule, mood_pattern, response_style, availability, focus_time)
        time_pattern: Time pattern configuration
        context_data: Context data (preferences, settings)
        priority: Priority (1=high, 3=low)
    """
    return controller.replace_context(
        context_id=context_id,
        name=name,
        context_type=context_type,
        time_pattern=time_pattern,
        context_data=context_data,
        priority=priority,
    )


@mcp.tool()
def delete_context(context_id: str) -> str:
    """Deletes a temporal context

    Args:
        context_id: ID of the context to delete
    """
    return controller.delete_context(context_id=context_id)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
