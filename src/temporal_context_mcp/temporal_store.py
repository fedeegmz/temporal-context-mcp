import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import TemporalContext, ContextType, TimePattern


class TemporalStore:
    """Manejo de almacenamiento persistente para contextos temporales"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.contexts_file = self.data_dir / "temporal_contexts.json"
        self.contexts: list[TemporalContext] = []
        self.load_contexts()

    def load_contexts(self):
        """Carga contextos desde el archivo JSON"""
        if self.contexts_file.exists():
            try:
                with open(self.contexts_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.contexts = [
                        TemporalContext.model_validate(context_data)
                        for context_data in data
                    ]
            except Exception as e:
                print(f"Error cargando contextos: {e}")
                self.contexts = []
        else:
            # Crear contextos de ejemplo
            self._create_default_contexts()

    def save_contexts(self):
        """Guarda contextos al archivo JSON"""
        try:
            data = [context.model_dump(mode="json") for context in self.contexts]
            with open(self.contexts_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error guardando contextos: {e}")

    def add_context(self, context: TemporalContext) -> bool:
        """Añade un nuevo contexto"""
        try:
            # Verificar que no existe un contexto con el mismo ID
            if any(c.id == context.id for c in self.contexts):
                return False

            self.contexts.append(context)
            self.save_contexts()
            return True
        except Exception:
            return False

    def update_context(self, context_id: str, updates: dict[str, Any]) -> bool:
        """Actualiza un contexto existente"""
        for i, context in enumerate(self.contexts):
            if context.id == context_id:
                try:
                    # Crear una copia actualizada
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
        """Elimina un contexto"""
        original_length = len(self.contexts)
        self.contexts = [c for c in self.contexts if c.id != context_id]

        if len(self.contexts) < original_length:
            self.save_contexts()
            return True
        return False

    def get_context(self, context_id: str) -> TemporalContext | None:
        """Obtiene un contexto por ID"""
        for context in self.contexts:
            if context.id == context_id:
                return context
        return None

    def list_contexts(
            self, context_type: ContextType | None = None
    ) -> list[TemporalContext]:
        """Lista todos los contextos, opcionalmente filtrados por tipo"""
        if context_type:
            return [c for c in self.contexts if c.context_type == context_type]
        return self.contexts.copy()

    def mark_context_used(self, context_id: str):
        """Marca un contexto como usado recientemente"""
        for context in self.contexts:
            if context.id == context_id:
                context.last_used = datetime.now()
                self.save_contexts()
                break

    def _create_default_contexts(self):
        """Crea contextos de ejemplo para demostrar funcionalidad"""
        default_contexts = [
            TemporalContext(
                id="work_hours",
                name="Horario de trabajo",
                context_type=ContextType.WORK_SCHEDULE,
                time_pattern=TimePattern(
                    days_of_week=[1, 2, 3, 4, 5],  # Lun-Vie
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
                name="Tiempo de concentración matutino",
                context_type=ContextType.FOCUS_TIME,
                time_pattern=TimePattern(
                    days_of_week=[1, 2, 3, 4, 5], hour_range=(8, 11)
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
                name="Fin de semana relajado",
                context_type=ContextType.RESPONSE_STYLE,
                time_pattern=TimePattern(days_of_week=[0, 6]),  # Sáb-Dom
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
