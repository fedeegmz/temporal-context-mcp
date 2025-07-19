import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import ContextType, TemporalContext, TimePattern


class TemporalStore:
    """Management of persistent storage for temporal contexts"""

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.contexts_file = self.data_dir / "temporal_contexts.json"
        self.contexts: list[TemporalContext] = []
        self.load_contexts()

    def load_contexts(self) -> None:
        """Loads contexts from the JSON file"""
        if self.contexts_file.exists():
            try:
                with open(self.contexts_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.contexts = [
                        TemporalContext.model_validate(context_data)
                        for context_data in data
                    ]
            except Exception as e:
                print(f"Error loading contexts: {e}")
                self.contexts = []
        else:
            # Create example contexts
            self._create_default_contexts()

    def save_contexts(self) -> None:
        """Saves contexts to the JSON file"""
        try:
            data = [context.model_dump(mode="json") for context in self.contexts]
            with open(self.contexts_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving contexts: {e}")

    def add_context(self, context: TemporalContext) -> bool:
        """Adds a new context"""
        try:
            # Verify that no context exists with the same ID
            if any(c.id == context.id for c in self.contexts):
                return False

            self.contexts.append(context)
            self.save_contexts()
            return True
        except Exception:
            return False

    def update_context(self, context_id: str, updates: dict[str, Any]) -> bool:
        """Updates an existing context"""
        for i, context in enumerate(self.contexts):
            if context.id == context_id:
                try:
                    # Create an updated copy
                    context_dict = context.model_dump()
                    context_dict.update(updates)
                    updated_context = TemporalContext.model_validate(context_dict)

                    self.contexts[i] = updated_context
                    self.save_contexts()
                    return True
                except Exception:
                    return False
        return False

    def delete_context(self, context_id: str) -> bool:
        """Deletes a context"""
        original_length = len(self.contexts)
        self.contexts = [c for c in self.contexts if c.id != context_id]

        if len(self.contexts) < original_length:
            self.save_contexts()
            return True
        return False

    def get_context(self, context_id: str) -> TemporalContext | None:
        """Gets a context by ID"""
        for context in self.contexts:
            if context.id == context_id:
                return context
        return None

    def list_contexts(
        self,
        context_type: ContextType | None = None,
    ) -> list[TemporalContext]:
        """Lists all contexts, optionally filtered by type"""
        if context_type:
            return [c for c in self.contexts if c.context_type == context_type]
        return self.contexts.copy()

    def mark_context_used(self, context_id: str) -> None:
        """Marks a context as recently used"""
        for context in self.contexts:
            if context.id == context_id:
                context.last_used = datetime.now()
                self.save_contexts()
                break

    def _create_default_contexts(self) -> None:
        """Creates example contexts to demonstrate functionality"""
        default_contexts = [
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
                created_at=datetime.now(),
            ),
            TemporalContext(
                id="focus_morning",
                name="Morning Focus Time",
                context_type=ContextType.FOCUS_TIME,
                time_pattern=TimePattern(
                    days_of_week=[1, 2, 3, 4, 5],
                    hour_range=(8, 11),
                ),
                context_data={
                    "preferences": {
                        "response_style": "concise",
                        "detail_level": "medium",
                    },
                    "avoid_interruptions": True,
                    "quick_responses_preferred": True,
                },
                created_at=datetime.now(),
            ),
            TemporalContext(
                id="weekend_casual",
                name="Relaxed Weekend",
                context_type=ContextType.RESPONSE_STYLE,
                time_pattern=TimePattern(days_of_week=[0, 6]),  # Sat-Sun
                context_data={
                    "preferences": {
                        "response_style": "casual",
                        "formality_level": "low",
                        "detail_level": "medium",
                    },
                    "encourage_creativity": True,
                    "suggested_topics": ["hobbies", "entertainment", "learning"],
                },
                created_at=datetime.now(),
            ),
        ]

        self.contexts = default_contexts
        self.save_contexts()
