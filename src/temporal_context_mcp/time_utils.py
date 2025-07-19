from datetime import datetime

import croniter
from dateutil import tz

from .models import TimePattern, TemporalContext


class TimeUtils:
    """Utilidades para manejo de tiempo y patrones temporales"""

    @staticmethod
    def get_current_datetime(timezone: str = "local") -> datetime:
        """Obtiene la fecha/hora actual en la zona horaria especificada"""
        if timezone == "local":
            return datetime.now(tz.tzlocal())
        else:
            return datetime.now(tz.gettz(timezone))

    @staticmethod
    def matches_time_pattern(pattern: TimePattern, target_time: datetime) -> bool:
        """Verifica si un momento específico coincide con el patrón de tiempo"""

        # Verificar días de la semana
        if pattern.days_of_week:
            # Python: 0=Lunes, 6=Domingo; Convertir a 0=Domingo
            weekday = (target_time.weekday() + 1) % 7
            if weekday not in pattern.days_of_week:
                return False

        # Verificar horas específicas
        if pattern.hours:
            if target_time.hour not in pattern.hours:
                return False

        # Verificar rango de horas
        if pattern.hour_range:
            start_hour, end_hour = pattern.hour_range
            if not (start_hour <= target_time.hour <= end_hour):
                return False

        # Verificar fechas específicas
        if pattern.specific_dates:
            date_str = target_time.strftime("%Y-%m-%d")
            if date_str not in pattern.specific_dates:
                return False

        # Verificar patrón cron
        if pattern.cron_pattern:
            try:
                cron = croniter.croniter(pattern.cron_pattern, target_time)
                # Si la próxima ejecución es exactamente ahora, coincide
                next_run = cron.get_next(datetime)
                return abs((next_run - target_time).total_seconds()) < 60
            except:
                return False

        return True

    @staticmethod
    def get_active_contexts(
            contexts: list[TemporalContext], target_time: datetime | None = None
    ) -> list[TemporalContext]:
        """Obtiene los contextos activos para un momento específico"""
        if target_time is None:
            target_time = TimeUtils.get_current_datetime()

        active_contexts = []
        for context in contexts:
            if context.active and TimeUtils.matches_time_pattern(
                    context.time_pattern, target_time
            ):
                active_contexts.append(context)

        # Ordenar por prioridad
        active_contexts.sort(key=lambda x: x.priority)
        return active_contexts

    @staticmethod
    def get_context_recommendations(active_contexts: list[TemporalContext]) -> dict:
        """Genera recomendaciones basadas en contextos activos"""
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
                    }
                )

            elif context.context_type == "focus_time":
                recommendations.update(
                    {
                        "response_style": "concise",
                        "detail_level": "low",
                        "avoid_topics": ["entertainment", "social_media"],
                        "time_sensitive": True,
                    }
                )

            elif context.context_type == "mood_pattern":
                mood = context_data.get("mood", "neutral")
                if mood == "creative":
                    recommendations.update(
                        {
                            "response_style": "inspiring",
                            "suggested_tools": ["brainstorm", "ideation", "research"],
                        }
                    )
                elif mood == "tired":
                    recommendations.update(
                        {"response_style": "gentle", "detail_level": "low"}
                    )

            # Aplicar configuraciones específicas del contexto
            if "preferences" in context_data:
                recommendations.update(context_data["preferences"])

        return recommendations

    @staticmethod
    def format_time_pattern_description(pattern: TimePattern) -> str:
        """Genera una descripción legible del patrón de tiempo"""
        descriptions = []

        if pattern.days_of_week:
            days_map = {
                0: "Dom",
                1: "Lun",
                2: "Mar",
                3: "Mié",
                4: "Jue",
                5: "Vie",
                6: "Sáb",
            }
            days = [days_map[d] for d in pattern.days_of_week]
            descriptions.append(f"Días: {', '.join(days)}")

        if pattern.hour_range:
            start, end = pattern.hour_range
            descriptions.append(f"Horario: {start:02d}:00-{end:02d}:00")

        if pattern.hours:
            hours_str = ", ".join([f"{h:02d}:00" for h in pattern.hours])
            descriptions.append(f"Horas: {hours_str}")

        if pattern.cron_pattern:
            descriptions.append(f"Patrón: {pattern.cron_pattern}")

        return " | ".join(descriptions) if descriptions else "Siempre activo"
