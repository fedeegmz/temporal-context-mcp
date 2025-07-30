from enum import IntEnum, unique


@unique
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
