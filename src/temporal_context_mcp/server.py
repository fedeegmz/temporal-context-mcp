from mcp.server.fastmcp import FastMCP

from temporal_context_mcp.context_management import (
    Controller,
    TemporalContextRepository,
    TemporalContextRepositoryImpl,
)
from temporal_context_mcp.context_management.application.dto import (
    TemporalContextResultDto,
)

mcp = FastMCP("temporal-context-mcp")

context_repository: TemporalContextRepository = TemporalContextRepositoryImpl()
controller = Controller()


@mcp.tool()
def get_current_context() -> TemporalContextResultDto | None:
    """Gets the current temporal context and recommendations"""
    return controller.get_current_context()


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


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
