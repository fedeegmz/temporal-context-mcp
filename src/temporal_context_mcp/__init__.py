"""
Temporal Context MCP Server

Un servidor MCP que proporciona contexto temporal inteligente
para adaptar respuestas según el momento y las rutinas del usuario.
"""

__version__ = "0.1.0"
__author__ = "Tu Nombre"
__description__ = "Servidor MCP para contexto temporal inteligente"

from .models import TemporalContext, ContextType, TimePattern, ContextResponse
from .server import TemporalContextServer
from .temporal_store import TemporalStore
from .time_utils import TimeUtils

__all__ = [
    "TemporalContext",
    "ContextType",
    "TimePattern",
    "ContextResponse",
    "TemporalStore",
    "TimeUtils",
    "TemporalContextServer",
]
