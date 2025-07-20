"""
Temporal Context MCP Server

A MCP server that provides intelligent temporal context to adapt responses
according to the user's time and routines.
"""

__version__ = "0.1.0"
__author__ = "Federico Gomez"
__description__ = "MCP server for intelligent temporal context"

from .context_repository import ContextRepository
from .models import ContextType, TemporalContext, TimePattern
from .recommendation_repository import RecommendationRepository
from .time_utils import TimeUtils

__all__ = [
    "ContextRepository",
    "ContextType",
    "RecommendationRepository",
    "TemporalContext",
    "TimePattern",
    "TimeUtils",
]
