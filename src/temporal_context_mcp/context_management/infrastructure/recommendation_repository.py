from temporal_context_mcp.core import settings
from temporal_context_mcp.recommendation import RecommendationRepositoryImpl
from temporal_context_mcp.shared import ContextType


class RecommendationRepository:
    def __init__(self) -> None:
        self.repository = RecommendationRepositoryImpl(settings=settings)

    def find_by_context_type(self, context_type: ContextType) -> dict[str, str] | None:
        recommendation = self.repository.find_by_context_type(context_type)
        if recommendation:
            return recommendation.model_dump(mode="json")
        return None
