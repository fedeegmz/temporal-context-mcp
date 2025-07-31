from pathlib import Path
from typing import override

from temporal_context_mcp.core import Settings
from temporal_context_mcp.recommendation import (
    DetailLevel,
    FormalityLevel,
    Recommendation,
    RecommendationRepository,
    ResponseStyle,
)
from temporal_context_mcp.shared import (
    ContextType,
    load_models_from_json_file,
    save_models_to_json_file,
)


class RecommendationRepositoryImpl(RecommendationRepository):
    def __init__(self, settings: Settings) -> None:
        self.data_dir = Path(settings.data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.recommendations_file = self.data_dir / settings.recommendations_file_name
        self.recommendations: list[Recommendation] = []
        self.__load_recommendations()

    @override
    def find_by_context_type(self, context_type: ContextType) -> Recommendation | None:
        for rec in self.recommendations:
            if rec.context_type == context_type:
                return rec
        return None

    def __load_recommendations(self) -> None:
        """Loads recommendations from the JSON file"""
        if self.recommendations_file.exists():
            try:
                self.recommendations = load_models_from_json_file(
                    file_path=str(self.recommendations_file),
                    model_class=Recommendation,
                )
            except Exception as e:
                print(f"Error loading recommendations: {e}")
                self.recommendations = []
                self.__save_recommendations()
        else:
            self.__create_default_recommendations()

    def __save_recommendations(self) -> None:
        """Saves recommendations to the JSON file"""
        try:
            save_models_to_json_file(
                file_path=str(self.recommendations_file),
                data=self.recommendations,
            )
        except Exception as e:
            print(f"Error saving recommendations: {e}")

    def __create_default_recommendations(self) -> None:
        """Creates example recommendations"""
        default_recommendations = [
            Recommendation(
                context_type=ContextType.WORK_SCHEDULE,
                response_style=ResponseStyle.PROFESSIONAL,
                formality_level=FormalityLevel.HIGH,
                detail_level=DetailLevel.MEDIUM,
            ),
            Recommendation(
                context_type=ContextType.FOCUS_TIME,
                response_style=ResponseStyle.CONCISE,
                formality_level=FormalityLevel.LOW,
                detail_level=DetailLevel.MEDIUM,
            ),
            Recommendation(
                context_type=ContextType.MOOD_PATTERN,
                response_style=ResponseStyle.CONCISE,
                formality_level=FormalityLevel.LOW,
                detail_level=DetailLevel.HIGH,
            ),
        ]

        self.recommendations = default_recommendations
        self.__save_recommendations()
