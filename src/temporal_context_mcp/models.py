from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class ContextType(str, Enum):
    WORK_SCHEDULE = "work_schedule"
    MOOD_PATTERN = "mood_pattern"
    RESPONSE_STYLE = "response_style"
    AVAILABILITY = "availability"
    FOCUS_TIME = "focus_time"


class TimePattern(BaseModel):
    """Define patrones de tiempo usando formato cron-like"""

    # Días de la semana (0=Domingo, 6=Sábado)
    days_of_week: list[int] | None = None
    # Horas específicas
    hours: list[int] | None = None
    # Rango de horas (ej: 9-17 para horario laboral)
    hour_range: tuple[int, int] | None = None
    # Fechas específicas
    specific_dates: list[str] | None = None  # ISO format
    # Patrón cron personalizado
    cron_pattern: str | None = None


class TemporalContext(BaseModel):
    """Contexto que se aplica en momentos específicos"""

    id: str
    name: str
    context_type: ContextType
    time_pattern: TimePattern
    context_data: dict[str, Any]
    active: bool = True
    created_at: datetime
    last_used: datetime | None = None
    priority: int = 1  # 1=alta, 2=media, 3=baja


class ContextResponse(BaseModel):
    """Respuesta con contexto aplicado"""

    current_contexts: list[TemporalContext]
    recommendations: dict[str, Any]
    timestamp: datetime
