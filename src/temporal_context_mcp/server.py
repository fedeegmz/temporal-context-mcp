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

from .models import TemporalContext, ContextType, TimePattern, ContextResponse
from .temporal_store import TemporalStore
from .time_utils import TimeUtils


class TemporalContextServer:
    """Servidor MCP para contexto temporal inteligente"""

    def __init__(self):
        self.store = TemporalStore()
        self.server = Server("temporal-context-mcp")
        self._setup_tools()

    def _setup_tools(self):
        """Configura las herramientas disponibles"""

        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            return ListToolsResult(
                tools=[
                    Tool(
                        name="get_current_context",
                        description="Obtiene el contexto temporal actual y recomendaciones",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "timezone": {
                                    "type": "string",
                                    "description": "Zona horaria (opcional, default: local)",
                                    "default": "local",
                                }
                            },
                        },
                    ),
                    Tool(
                        name="add_temporal_context",
                        description="Añade un nuevo contexto temporal",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "ID único del contexto",
                                },
                                "name": {
                                    "type": "string",
                                    "description": "Nombre descriptivo",
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
                                    "description": "Tipo de contexto",
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
                                            "description": "Días de la semana (0=Domingo, 6=Sábado)",
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
                                            "description": "Rango de horas [inicio, fin]",
                                        },
                                        "hours": {
                                            "type": "array",
                                            "items": {
                                                "type": "integer",
                                                "minimum": 0,
                                                "maximum": 23,
                                            },
                                            "description": "Horas específicas",
                                        },
                                        "cron_pattern": {
                                            "type": "string",
                                            "description": "Patrón cron personalizado",
                                        },
                                    },
                                },
                                "context_data": {
                                    "type": "object",
                                    "description": "Datos del contexto (preferencias, configuraciones)",
                                },
                                "priority": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 3,
                                    "default": 1,
                                    "description": "Prioridad (1=alta, 3=baja)",
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
                        description="Lista todos los contextos temporales",
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
                                    "description": "Filtrar por tipo de contexto (opcional)",
                                },
                                "active_only": {
                                    "type": "boolean",
                                    "default": False,
                                    "description": "Solo contextos actualmente activos",
                                },
                            },
                        },
                    ),
                    Tool(
                        name="update_context",
                        description="Actualiza un contexto temporal existente",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "context_id": {
                                    "type": "string",
                                    "description": "ID del contexto a actualizar",
                                },
                                "updates": {
                                    "type": "object",
                                    "description": "Campos a actualizar",
                                },
                            },
                            "required": ["context_id", "updates"],
                        },
                    ),
                    Tool(
                        name="delete_context",
                        description="Elimina un contexto temporal",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "context_id": {
                                    "type": "string",
                                    "description": "ID del contexto a eliminar",
                                }
                            },
                            "required": ["context_id"],
                        },
                    ),
                    Tool(
                        name="preview_context",
                        description="Previsualiza qué contextos estarían activos en un momento específico",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "datetime": {
                                    "type": "string",
                                    "description": "Fecha y hora ISO (opcional, default: ahora)",
                                },
                                "timezone": {
                                    "type": "string",
                                    "default": "local",
                                    "description": "Zona horaria",
                                },
                            },
                        },
                    ),
                ]
            )

        @self.server.call_tool()
        async def call_tool(request: CallToolRequest) -> CallToolResult:
            try:
                if request.name == "get_current_context":
                    return await self._get_current_context(request.arguments or {})
                elif request.name == "add_temporal_context":
                    return await self._add_temporal_context(request.arguments or {})
                elif request.name == "list_contexts":
                    return await self._list_contexts(request.arguments or {})
                elif request.name == "update_context":
                    return await self._update_context(request.arguments or {})
                elif request.name == "delete_context":
                    return await self._delete_context(request.arguments or {})
                elif request.name == "preview_context":
                    return await self._preview_context(request.arguments or {})
                else:
                    raise ValueError(f"Herramienta desconocida: {request.name}")

            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

    async def _get_current_context(self, args: dict) -> CallToolResult:
        """Obtiene el contexto temporal actual"""
        timezone = args.get("timezone", "local")
        current_time = TimeUtils.get_current_datetime(timezone)

        active_contexts = TimeUtils.get_active_contexts(
            self.store.contexts, current_time
        )
        recommendations = TimeUtils.get_context_recommendations(active_contexts)

        # Marcar contextos como usados
        for context in active_contexts:
            self.store.mark_context_used(context.id)

        response = ContextResponse(
            current_contexts=active_contexts,
            recommendations=recommendations,
            timestamp=current_time,
        )

        result_text = f"""🕒 **Contexto Temporal Actual** ({current_time.strftime('%Y-%m-%d %H:%M:%S')})

**Contextos Activos:** {len(active_contexts)}
"""

        for context in active_contexts:
            pattern_desc = TimeUtils.format_time_pattern_description(
                context.time_pattern
            )
            result_text += f"""
• **{context.name}** ({context.context_type})
  - Patrón: {pattern_desc}
  - Prioridad: {context.priority}
"""

        result_text += f"""
**Recomendaciones:**
• Estilo de respuesta: {recommendations['response_style']}
• Nivel de formalidad: {recommendations['formality_level']}
• Nivel de detalle: {recommendations['detail_level']}
• Sensible al tiempo: {recommendations['time_sensitive']}
"""

        if recommendations["suggested_tools"]:
            result_text += f"• Herramientas sugeridas: {', '.join(recommendations['suggested_tools'])}\n"

        if recommendations["avoid_topics"]:
            result_text += (
                f"• Evitar temas: {', '.join(recommendations['avoid_topics'])}\n"
            )

        return CallToolResult(content=[TextContent(type="text", text=result_text)])

    async def _add_temporal_context(self, args: dict) -> CallToolResult:
        """Añade un nuevo contexto temporal"""
        try:
            # Convertir hour_range de lista a tupla si existe
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
                            text=f"✅ Contexto '{context.name}' añadido exitosamente.\nPatrón: {pattern_desc}",
                        )
                    ]
                )
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"❌ Error: Ya existe un contexto con ID '{args['id']}'",
                        )
                    ]
                )

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", text=f"❌ Error creando contexto: {str(e)}"
                    )
                ]
            )

    async def _list_contexts(self, args: dict) -> CallToolResult:
        """Lista contextos temporales"""
        context_type = args.get("context_type")
        active_only = args.get("active_only", False)

        if context_type:
            contexts = self.store.list_contexts(ContextType(context_type))
        else:
            contexts = self.store.list_contexts()

        if active_only:
            current_time = TimeUtils.get_current_datetime()
            contexts = TimeUtils.get_active_contexts(contexts, current_time)

        result_text = f"📋 **Contextos Temporales** ({len(contexts)} encontrados)\n\n"

        for context in contexts:
            status = "🟢 Activo" if context.active else "🔴 Inactivo"
            pattern_desc = TimeUtils.format_time_pattern_description(
                context.time_pattern
            )
            last_used = (
                context.last_used.strftime("%Y-%m-%d %H:%M")
                if context.last_used
                else "Nunca"
            )

            result_text += f"""**{context.name}** ({context.id})
• Tipo: {context.context_type}
• Estado: {status}
• Patrón: {pattern_desc}
• Prioridad: {context.priority}
• Último uso: {last_used}
• Datos: {len(context.context_data)} configuraciones

"""

        return CallToolResult(content=[TextContent(type="text", text=result_text)])

    async def _update_context(self, args: dict) -> CallToolResult:
        """Actualiza un contexto temporal"""
        context_id = args["context_id"]
        updates = args["updates"]

        success = self.store.update_context(context_id, updates)

        if success:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"✅ Contexto '{context_id}' actualizado exitosamente.",
                    )
                ]
            )
        else:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Error: No se encontró el contexto '{context_id}'",
                    )
                ]
            )

    async def _delete_context(self, args: dict) -> CallToolResult:
        """Elimina un contexto temporal"""
        context_id = args["context_id"]

        # Verificar que existe antes de eliminar
        context = self.store.get_context(context_id)
        if not context:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Error: No se encontró el contexto '{context_id}'",
                    )
                ]
            )

        success = self.store.delete_context(context_id)

        if success:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"✅ Contexto '{context.name}' ({context_id}) eliminado exitosamente.",
                    )
                ]
            )
        else:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text", text=f"❌ Error eliminando contexto '{context_id}'"
                    )
                ]
            )

    async def _preview_context(self, args: dict) -> CallToolResult:
        """Previsualiza contextos activos en un momento específico"""
        timezone = args.get("timezone", "local")

        if args.get("datetime"):
            try:
                target_time = datetime.fromisoformat(args["datetime"])
            except ValueError:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="❌ Error: Formato de fecha/hora inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
                        )
                    ]
                )
        else:
            target_time = TimeUtils.get_current_datetime(timezone)

        active_contexts = TimeUtils.get_active_contexts(
            self.store.contexts, target_time
        )
        recommendations = TimeUtils.get_context_recommendations(active_contexts)

        result_text = f"""🔮 **Previsualización de Contexto**
📅 Fecha/Hora: {target_time.strftime('%Y-%m-%d %H:%M:%S')}
🌍 Zona Horaria: {timezone}

**Contextos que estarían activos:** {len(active_contexts)}
"""

        for context in active_contexts:
            pattern_desc = TimeUtils.format_time_pattern_description(
                context.time_pattern
            )
            result_text += f"""
• **{context.name}** ({context.context_type})
  - Patrón: {pattern_desc}
  - Prioridad: {context.priority}
"""

        if not active_contexts:
            result_text += "\n• No hay contextos activos en este momento"
        else:
            result_text += f"""
**Recomendaciones que se aplicarían:**
• Estilo: {recommendations['response_style']}
• Formalidad: {recommendations['formality_level']}
• Detalle: {recommendations['detail_level']}
• Urgente: {recommendations['time_sensitive']}
"""

            if recommendations["suggested_tools"]:
                result_text += (
                    f"• Herramientas: {', '.join(recommendations['suggested_tools'])}\n"
                )

            if recommendations["avoid_topics"]:
                result_text += (
                    f"• Evitar: {', '.join(recommendations['avoid_topics'])}\n"
                )

        return CallToolResult(content=[TextContent(type="text", text=result_text)])


async def main():
    """Función principal para ejecutar el servidor"""
    server_instance = TemporalContextServer()

    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="temporal-context-mcp",
                server_version="0.1.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None, experimental_capabilities=None
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
