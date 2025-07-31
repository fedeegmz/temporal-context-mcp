from pydantic import BaseModel, Field

from temporal_context_mcp.recommendation.domain.value_object.detail_level import (
    DetailLevel,
)
from temporal_context_mcp.recommendation.domain.value_object.formality_level import (
    FormalityLevel,
)
from temporal_context_mcp.recommendation.domain.value_object.response_style import (
    ResponseStyle,
)
from temporal_context_mcp.shared import ContextType


class Recommendation(BaseModel):
    context_type: ContextType = Field(...)
    response_style: ResponseStyle = Field(default=ResponseStyle.NORMAL)
    formality_level: FormalityLevel = Field(default=FormalityLevel.MEDIUM)
    detail_level: DetailLevel = Field(default=DetailLevel.MEDIUM)
    suggested_tools: list[str] = Field(default=[])
    avoid_topics: list[str] = Field(default=[])
    time_sensitive: bool = Field(default=False)
