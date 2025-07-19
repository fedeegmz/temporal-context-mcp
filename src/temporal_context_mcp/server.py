import asyncio
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

from .models import ContextResponse, ContextType, TemporalContext, TimePattern
from .temporal_store import TemporalStore
from .time_utils import TimeUtils


class TemporalContextServer:
    """MCP server for intelligent temporal context"""

    def __init__(self) -> None:
        self.store = TemporalStore()
        self.server = Server("temporal-context-mcp")
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Sets up the available tools"""

        @self.server.list_tools()
        def list_tools() -> ListToolsResult:
            return ListToolsResult(
                tools=[
                    Tool(
                        name="get_current_context",
                        description="Gets the current temporal context and recommendations",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "timezone": {
                                    "type": "string",
                                    "description": "Timezone (optional, default: local)",
                                    "default": "local",
                                },
                            },
                        },
                    ),
                    Tool(
                        name="add_temporal_context",
                        description="Adds a new temporal context",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "Unique context ID",
                                },
                                "name": {
                                    "type": "string",
                                    "description": "Descriptive name",
                                },
                                "context_type": {
                                    "type": "string",
                                    "enum": [
                                        "work_schedule",
                                        "mood_pattern",
                                        "response_style",
                                        "availability",
                                        "focus_time",
                                    ],
                                    "description": "Context type",
                                },
                                "time_pattern": {
                                    "type": "object",
                                    "properties": {
                                        "days_of_week": {
                                            "type": "array",
                                            "items": {
                                                "type": "integer",
                                                "minimum": 0,
                                                "maximum": 6,
                                            },
                                            "description": "Days of the week (0=Sunday, 6=Saturday)",
                                        },
                                        "hour_range": {
                                            "type": "array",
                                            "items": {
                                                "type": "integer",
                                                "minimum": 0,
                                                "maximum": 23,
                                            },
                                            "minItems": 2,
                                            "maxItems": 2,
                                            "description": "Hour range [start, end]",
                                        },
                                        "hours": {
                                            "type": "array",
                                            "items": {
                                                "type": "integer",
                                                "minimum": 0,
                                                "maximum": 23,
                                            },
                                            "description": "Specific hours",
                                        },
                                        "cron_pattern": {
                                            "type": "string",
                                            "description": "Custom cron pattern",
                                        },
                                    },
                                },
                                "context_data": {
                                    "type": "object",
                                    "description": "Context data (preferences, settings)",
                                },
                                "priority": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 3,
                                    "default": 1,
                                    "description": "Priority (1=high, 3=low)",
                                },
                            },
                            "required": [
                                "id",
                                "name",
                                "context_type",
                                "time_pattern",
                                "context_data",
                            ],
                        },
                    ),
                    Tool(
                        name="list_contexts",
                        description="Lists all temporal contexts",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "context_type": {
                                    "type": "string",
                                    "enum": [
                                        "work_schedule",
                                        "mood_pattern",
                                        "response_style",
                                        "availability",
                                        "focus_time",
                                    ],
                                    "description": "Filter by context type (optional)",
                                },
                                "active_only": {
                                    "type": "boolean",
                                    "default": False,
                                    "description": "Only currently active contexts",
                                },
                            },
                        },
                    ),
                    Tool(
                        name="update_context",
                        description="Updates an existing temporal context",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "context_id": {
                                    "type": "string",
                                    "description": "ID of the context to update",
                                },
                                "updates": {
                                    "type": "object",
                                    "description": "Fields to update",
                                },
                            },
                            "required": ["context_id", "updates"],
                        },
                    ),
                    Tool(
                        name="delete_context",
                        description="Deletes a temporal context",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "context_id": {
                                    "type": "string",
                                    "description": "ID of the context to delete",
                                },
                            },
                            "required": ["context_id"],
                        },
                    ),
                    Tool(
                        name="preview_context",
                        description="Previews which contexts would be active at a specific time",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "datetime": {
                                    "type": "string",
                                    "description": "ISO datetime (optional, default: now)",
                                },
                                "timezone": {
                                    "type": "string",
                                    "default": "local",
                                    "description": "Timezone",
                                },
                            },
                        },
                    ),
                ],
            )

        @self.server.call_tool()
        async def call_tool(request: CallToolRequest) -> CallToolResult:
            try:
                if request.name == "get_current_context":
                    return await self._get_current_context(request.arguments or {})
                if request.name == "add_temporal_context":
                    return await self._add_temporal_context(request.arguments or {})
                if request.name == "list_contexts":
                    return await self._list_contexts(request.arguments or {})
                if request.name == "update_context":
                    return await self._update_context(request.arguments or {})
                if request.name == "delete_context":
                    return await self._delete_context(request.arguments or {})
                if request.name == "preview_context":
                    return await self._preview_context(request.arguments or {})
                raise ValueError(f"Unknown tool: {request.name}")

            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {e!s}")],
                )

    async def _get_current_context(self, args: dict) -> CallToolResult:
        """Gets the current temporal context"""
        timezone = args.get("timezone", "local")
        current_time = TimeUtils.get_current_datetime(timezone)

        active_contexts = TimeUtils.get_active_contexts(
            self.store.contexts,
            current_time,
        )
        recommendations = TimeUtils.get_context_recommendations(active_contexts)

        # Mark contexts as used
        for context in active_contexts:
            self.store.mark_context_used(context.id)

        response = ContextResponse(
            current_contexts=active_contexts,
            recommendations=recommendations,
            timestamp=current_time,
        )

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
            result_text += (
                f"• Avoid topics: {', '.join(recommendations['avoid_topics'])}\n"
            )

        return CallToolResult(content=[TextContent(type="text", text=result_text)])

    async def _add_temporal_context(self, args: dict) -> CallToolResult:
        """Adds a new temporal context"""
        try:
            # Convert hour_range from list to tuple if it exists
            if "time_pattern" in args and "hour_range" in args["time_pattern"]:
                hour_range = args["time_pattern"]["hour_range"]
                if isinstance(hour_range, list) and len(hour_range) == 2:
                    args["time_pattern"]["hour_range"] = tuple(hour_range)

            time_pattern = TimePattern(**args["time_pattern"])

            context = TemporalContext(
                id=args["id"],
                name=args["name"],
                context_type=ContextType(args["context_type"]),
                time_pattern=time_pattern,
                context_data=args["context_data"],
                priority=args.get("priority", 1),
                created_at=datetime.now(),
            )

            success = self.store.add_context(context)

            if success:
                pattern_desc = TimeUtils.format_time_pattern_description(time_pattern)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"✅ Context '{context.name}' successfully added.\nPattern: {pattern_desc}",
                        ),
                    ],
                )
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Error: A context with ID '{args['id']}' already exists",
                    ),
                ],
            )

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Error creating context: {e!s}",
                    ),
                ],
            )

    async def _list_contexts(self, args: dict) -> CallToolResult:
        """Lists temporal contexts"""
        context_type = args.get("context_type")
        active_only = args.get("active_only", False)

        if context_type:
            contexts = self.store.list_contexts(ContextType(context_type))
        else:
            contexts = self.store.list_contexts()

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

        return CallToolResult(content=[TextContent(type="text", text=result_text)])

    async def _update_context(self, args: dict) -> CallToolResult:
        """Updates a temporal context"""
        context_id = args["context_id"]
        updates = args["updates"]

        success = self.store.update_context(context_id, updates)

        if success:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"✅ Context '{context_id}' successfully updated.",
                    ),
                ],
            )
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"❌ Error: Context '{context_id}' not found",
                ),
            ],
        )

    async def _delete_context(self, args: dict) -> CallToolResult:
        """Deletes a temporal context"""
        context_id = args["context_id"]

        # Verify that the context exists before deleting
        context = self.store.get_context(context_id)
        if not context:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Error: Context '{context_id}' not found",
                    ),
                ],
            )

        success = self.store.delete_context(context_id)

        if success:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"✅ Context '{context.name}' ({context_id}) successfully deleted.",
                    ),
                ],
            )
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"❌ Error deleting context '{context_id}'",
                ),
            ],
        )

    async def _preview_context(self, args: dict) -> CallToolResult:
        """Previews active contexts at a specific time"""
        timezone = args.get("timezone", "local")

        if args.get("datetime"):
            try:
                target_time = datetime.fromisoformat(args["datetime"])
            except ValueError:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="❌ Error: Invalid date/time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
                        ),
                    ],
                )
        else:
            target_time = TimeUtils.get_current_datetime(timezone)

        active_contexts = TimeUtils.get_active_contexts(
            self.store.contexts,
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
                result_text += (
                    f"• Tools: {', '.join(recommendations['suggested_tools'])}\n"
                )

            if recommendations["avoid_topics"]:
                result_text += (
                    f"• Avoid: {', '.join(recommendations['avoid_topics'])}\n"
                )

        return CallToolResult(content=[TextContent(type="text", text=result_text)])


async def main() -> None:
    """Main function to run the server"""
    server_instance = TemporalContextServer()

    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="temporal-context-mcp",
                server_version="0.1.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
