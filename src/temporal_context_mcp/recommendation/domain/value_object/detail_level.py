from enum import Enum, unique


@unique
class DetailLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
