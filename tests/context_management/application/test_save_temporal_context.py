from temporal_context_mcp.context_management.application import SaveTemporalContext
from temporal_context_mcp.context_management.application.dto import (
    SaveTemporalContextDto,
)
from temporal_context_mcp.shared import ContextType, TimePattern


def test_save_temporal_context_should_return_true_if_dto_is_valid(
    mock_save_temporal_context: SaveTemporalContext,
) -> None:
    valid_dto = SaveTemporalContextDto(
        id="valid-id-123",
        name="My test context",
        context_type=ContextType.FOCUS_TIME,
        time_pattern=TimePattern(days_of_week=[2]),
    )
    result = mock_save_temporal_context.execute(dto=valid_dto)
    assert result is True
