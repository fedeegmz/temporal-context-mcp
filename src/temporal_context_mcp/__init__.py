"""
Temporal Context MCP Server

A MCP server that provides intelligent temporal context to adapt responses
according to the user's time and routines.
"""

__version__ = "0.1.0"
__author__ = "Federico Gomez"
__description__ = "MCP server for intelligent temporal context"

from .models import ContextResponse, ContextType, TemporalContext, TimePattern
from .server import TemporalContextServer
from .temporal_store import TemporalStore
from .time_utils import TimeUtils

__all__ = [
    "ContextResponse",
    "ContextType",
    "TemporalContext",
    "TemporalContextServer",
    "TemporalStore",
    "TimePattern",
    "TimeUtils",
]
