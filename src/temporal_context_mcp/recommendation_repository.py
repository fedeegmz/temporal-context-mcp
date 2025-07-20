from temporal_context_mcp import TemporalContext


class RecommendationRepository:
    @staticmethod
    def get_context_recommendations(active_contexts: list[TemporalContext]) -> dict:
        """Generates recommendations based on active contexts"""
        recommendations = {
            "response_style": "normal",
            "formality_level": "medium",
            "detail_level": "medium",
            "suggested_tools": [],
            "avoid_topics": [],
            "time_sensitive": False,
        }

        for context in active_contexts:
            context_data = context.context_data

            if context.context_type == "work_schedule":
                recommendations.update(
                    {
                        "response_style": "professional",
                        "formality_level": "high",
                        "suggested_tools": ["calendar", "task_manager", "email"],
                        "time_sensitive": True,
                    },
                )

            elif context.context_type == "focus_time":
                recommendations.update(
                    {
                        "response_style": "concise",
                        "detail_level": "low",
                        "avoid_topics": ["entertainment", "social_media"],
                        "time_sensitive": True,
                    },
                )

            elif context.context_type == "mood_pattern":
                mood = context_data.get("mood", "neutral")
                if mood == "creative":
                    recommendations.update(
                        {
                            "response_style": "inspiring",
                            "suggested_tools": ["brainstorm", "ideation", "research"],
                        },
                    )
                elif mood == "tired":
                    recommendations.update(
                        {"response_style": "gentle", "detail_level": "low"},
                    )

            # Apply specific context configurations
            if "preferences" in context_data:
                recommendations.update(context_data["preferences"])

        return recommendations
