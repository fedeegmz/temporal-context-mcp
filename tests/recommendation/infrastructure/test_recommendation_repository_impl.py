from pathlib import Path

from temporal_context_mcp.core import Settings
from temporal_context_mcp.recommendation import (
    DetailLevel,
    FormalityLevel,
    RecommendationRepositoryImpl,
    ResponseStyle,
)
from temporal_context_mcp.shared import ContextType


def test_init_repository_creates_recommendations_file_if_not_exists(
    mock_settings: Settings,
) -> None:
    recommendations_file = (
        Path(mock_settings.data_dir) / mock_settings.recommendations_file_name
    )
    assert not recommendations_file.exists()

    _ = RecommendationRepositoryImpl(settings=mock_settings)

    assert recommendations_file.exists()


def test_init_repository_creates_empty_list_for_invalid_json(
    mock_settings: Settings,
) -> None:
    recommendations_file = (
        Path(mock_settings.data_dir) / mock_settings.recommendations_file_name
    )
    recommendations_file.write_text("invalid json")

    repository = RecommendationRepositoryImpl(settings=mock_settings)
    recommendations = repository.recommendations

    assert len(recommendations) == 0


def test_init_repository_creates_recommendations_file_with_default_data(
    mock_settings: Settings,
) -> None:
    repository = RecommendationRepositoryImpl(settings=mock_settings)

    recommendations = repository.recommendations

    assert len(recommendations) == 3
    assert recommendations[0].context_type == ContextType.WORK_SCHEDULE
    assert recommendations[0].response_style == ResponseStyle.PROFESSIONAL
    assert recommendations[0].formality_level == FormalityLevel.HIGH
    assert recommendations[0].detail_level == DetailLevel.MEDIUM
    assert recommendations[1].context_type == ContextType.FOCUS_TIME
    assert recommendations[1].response_style == ResponseStyle.CONCISE
    assert recommendations[1].formality_level == FormalityLevel.LOW
    assert recommendations[1].detail_level == DetailLevel.MEDIUM
    assert recommendations[2].context_type == ContextType.MOOD_PATTERN
    assert recommendations[2].response_style == ResponseStyle.CONCISE
    assert recommendations[2].formality_level == FormalityLevel.LOW
    assert recommendations[2].detail_level == DetailLevel.HIGH


def test_find_by_context_type_returns_matching_recommendation(
    mock_settings: Settings,
) -> None:
    repository = RecommendationRepositoryImpl(settings=mock_settings)

    result = repository.find_by_context_type(ContextType.WORK_SCHEDULE)

    assert result.context_type == ContextType.WORK_SCHEDULE
    assert result.response_style == ResponseStyle.PROFESSIONAL
    assert result.formality_level == FormalityLevel.HIGH
    assert result.detail_level == DetailLevel.MEDIUM


def test_find_by_context_types_returns_none_for_no_matches(
    mock_settings: Settings,
) -> None:
    repository = RecommendationRepositoryImpl(settings=mock_settings)

    result = repository.find_by_context_type(ContextType.AVAILABILITY)

    assert result is None
