import pytest

from temporal_context_mcp.context_management import TemporalContextRepository
from temporal_context_mcp.context_management.application import SaveTemporalContext
from temporal_context_mcp.context_management.domain import TemporalContext
from temporal_context_mcp.shared import ContextType


class MockTemporalContextRepository(TemporalContextRepository):
    def __init__(self) -> None:
        self.data: list[TemporalContext] = []

    def find_one_by_id(self, context_id: str) -> TemporalContext | None:
        pass

    def find(
        self,
        context_type: ContextType | None = None,
        actives: bool | None = None,
    ) -> list[TemporalContext]:
        pass

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


@pytest.fixture
def mock_temporal_context_repository() -> TemporalContextRepository:
    return MockTemporalContextRepository()


@pytest.fixture
def mock_save_temporal_context(
    mock_temporal_context_repository: TemporalContextRepository,
) -> SaveTemporalContext:
    return SaveTemporalContext(
        temporal_context_repository=mock_temporal_context_repository,
    )
