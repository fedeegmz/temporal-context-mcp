from abc import ABC, abstractmethod

from temporal_context_mcp.app.infrastructure.temporal_context_repository_impl import (
    TemporalContext,
)


class RecommendationRepository(ABC):
    @staticmethod
    @abstractmethod
    def get_context_recommendations(active_contexts: list[TemporalContext]) -> dict:
        """Generates recommendations based on active contexts"""
