from abc import ABC, abstractmethod

from temporal_context_mcp.recommendation.domain.recommendation import Recommendation
from temporal_context_mcp.shared import ContextType


class RecommendationRepository(ABC):
    @abstractmethod
    def find_by_context_type(self, context_type: ContextType) -> Recommendation | None:
        """Find all recommendations based on active context types"""
