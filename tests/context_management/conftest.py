from typing import Any

import pytest

from temporal_context_mcp.context_management import (
    RecommendationRepository,
    TemporalContextRepository,
)
from temporal_context_mcp.context_management.application import (
    FindCurrentTemporalContext,
    FindTemporalContext,
    SaveTemporalContext,
)
from temporal_context_mcp.context_management.domain import TemporalContext
from temporal_context_mcp.shared import ContextType, TimePattern, get_current_datetime


class MockTemporalContextRepository(TemporalContextRepository):
    def __init__(self) -> None:
        self.data: list[TemporalContext] = [
            TemporalContext(
                id="work_hours",
                name="Work Schedule",
                context_type=ContextType.WORK_SCHEDULE,
                time_pattern=TimePattern(
                    days_of_week=[1, 2, 3, 4, 5],  # Mon-Fri
                    hour_range=(9, 17),  # 9AM-5PM
                ),
                context_data={
                    "preferences": {
                        "response_style": "professional",
                        "formality_level": "high",
                        "detail_level": "high",
                    },
                    "suggested_tools": ["calendar", "email", "tasks"],
                    "avoid_topics": ["entertainment", "personal"],
                },
                created_at=get_current_datetime(),
            ),
        ]

    def find_one_by_id(self, context_id: str) -> TemporalContext | None:
        pass

    def find(
        self,
        context_type: ContextType | None = None,
        actives: bool | None = None,
    ) -> list[TemporalContext]:
        if context_type is not None:
            return [ctx for ctx in self.data if ctx.context_type == context_type]
        if actives is not None:
            return [ctx for ctx in self.data if ctx.active]
        return self.data

    def save(self, context: TemporalContext) -> bool:
        for item in self.data:
            if item.id == context.id:
                return False
        self.data.append(context)
        return True

    def delete_one_by_id(self, context_id: str) -> bool:
        pass

    def mark_one_as_used(self, context_id: str) -> None:
        pass


class MockRecommendationRepository(RecommendationRepository):
    def __init__(self) -> None:
        self.data: list[dict[str, Any]] = [
            {
                "context_type": ContextType.WORK_SCHEDULE.value,
                "response_style": "normal",
                "formality_level": "medium",
                "detail_level": "medium",
                "suggested_tools": [],
                "avoid_topics": [],
                "time_sensitive": False,
            },
        ]

    def find_by_context_type(self, context_type: ContextType) -> dict[str, str] | None:
        return next(
            (rec for rec in self.data if rec["context_type"] == context_type),
            None,
        )


@pytest.fixture
def mock_temporal_context_repository() -> TemporalContextRepository:
    return MockTemporalContextRepository()


@pytest.fixture
def mock_recommendation_repository() -> RecommendationRepository:
    return MockRecommendationRepository()


@pytest.fixture
def mock_save_temporal_context(
    mock_temporal_context_repository: TemporalContextRepository,
) -> SaveTemporalContext:
    return SaveTemporalContext(
        temporal_context_repository=mock_temporal_context_repository,
    )


@pytest.fixture
def mock_find_current_temporal_context(
    mock_temporal_context_repository: TemporalContextRepository,
    mock_recommendation_repository: RecommendationRepository,
) -> FindCurrentTemporalContext:
    return FindCurrentTemporalContext(
        temporal_context_repository=mock_temporal_context_repository,
        recommendation_repository=mock_recommendation_repository,
        find_temporal_context=FindTemporalContext(
            temporal_context_repository=mock_temporal_context_repository,
        ),
    )
