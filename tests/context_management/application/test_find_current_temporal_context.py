from temporal_context_mcp.context_management.application import (
    FindCurrentTemporalContext,
)


def test_find_current_temporal_context_should_return_current_temporal_context_with_recommendations(
    mock_find_current_temporal_context: FindCurrentTemporalContext,
) -> None:
    result = mock_find_current_temporal_context.execute()

    assert result is not None
    assert result.recommendation == {
        "context_type": "work_schedule",
        "response_style": "normal",
        "formality_level": "medium",
        "detail_level": "medium",
        "suggested_tools": [],
        "avoid_topics": [],
        "time_sensitive": False,
    }
