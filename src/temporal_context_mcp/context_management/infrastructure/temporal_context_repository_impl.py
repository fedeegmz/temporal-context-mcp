import json
from datetime import datetime
from pathlib import Path
from typing import override

from temporal_context_mcp.context_management.domain import (
    TemporalContext,
    TemporalContextRepository,
)
from temporal_context_mcp.shared import (
    ContextType,
    TimePattern,
    TimePatternUtils,
    default_false,
    get_current_datetime,
)


class TemporalContextRepositoryImpl(TemporalContextRepository):
    """Management of persistent storage for temporal contexts"""

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.contexts_file = self.data_dir / "temporal_contexts.json"
        self.contexts: list[TemporalContext] = []
        self.__load_contexts()

    @override
    def find_one_by_id(self, context_id: str) -> TemporalContext | None:
        """Gets a context by ID"""
        return next(
            (context for context in self.contexts if context.id == context_id),
            None,
        )

    @override
    def find(
        self,
        context_type: ContextType | None = None,
        actives: bool | None = None,
    ) -> list[TemporalContext]:
        """Lists all contexts, optionally filtered by type"""
        contexts = self.contexts.copy()
        if context_type is not None:
            contexts = [c for c in contexts if c.context_type == context_type]
        if actives is not None:
            current_time = get_current_datetime()
            contexts = [
                context
                for context in contexts
                if context.active
                and TimePatternUtils(
                    context.time_pattern,
                ).is_time_match(current_time)
            ]
        contexts.sort(key=lambda x: x.priority)
        return contexts

    @override
    @default_false
    def save(self, context: TemporalContext) -> bool:
        """Adds a new context"""
        if any(c.id == context.id for c in self.contexts):
            for i, ctx in enumerate(self.contexts):
                if ctx.id == context.id:
                    self.contexts[i] = context
                    self.__save_contexts()
                    return True
            return False

        self.contexts.append(context)
        self.__save_contexts()
        return True

    @override
    def delete_one_by_id(self, context_id: str) -> bool:
        """Deletes a context"""
        original_length = len(self.contexts)
        self.contexts = [c for c in self.contexts if c.id != context_id]

        if len(self.contexts) < original_length:
            self.__save_contexts()
            return True
        return False

    @override
    def mark_one_as_used(self, context_id: str) -> None:
        """Marks a context as recently used"""
        for context in self.contexts:
            if context.id == context_id:
                context.last_used = get_current_datetime()
                self.__save_contexts()
                break

    def __load_contexts(self) -> None:
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
                self.__save_contexts()
        else:
            self.__create_default_contexts()

    def __save_contexts(self) -> None:
        """Saves contexts to the JSON file"""
        try:
            data = [context.model_dump(mode="json") for context in self.contexts]
            with open(self.contexts_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving contexts: {e}")

    def __create_default_contexts(self) -> None:
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
        self.__save_contexts()
