from enum import Enum, unique


@unique
class FormalityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
