from abc import ABC, abstractmethod

from temporal_context_mcp.context_management.domain.temporal_context import (
    TemporalContext,
)
from temporal_context_mcp.shared import ContextType


class TemporalContextRepository(ABC):
    @abstractmethod
    def find_one_by_id(self, context_id: str) -> TemporalContext | None:
        """Gets a context by ID"""

    @abstractmethod
    def find(
        self,
        context_type: ContextType | None = None,
        actives: bool | None = None,
    ) -> list[TemporalContext]:
        """Lists all contexts, optionally filtered by type"""

    @abstractmethod
    def save(self, context: TemporalContext) -> bool:
        """Adds a new context"""

    @abstractmethod
    def delete_one_by_id(self, context_id: str) -> bool:
        """Deletes a context"""

    @abstractmethod
    def mark_one_as_used(self, context_id: str) -> None:
        """Marks a context as recently used"""
