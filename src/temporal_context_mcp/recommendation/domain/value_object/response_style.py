from enum import Enum, unique


@unique
class ResponseStyle(Enum):
    NORMAL = "normal"
    PROFESSIONAL = "professional"
    CONCISE = "concise"
    INSPIRING = "inspiring"
    GENTLE = "gentle"
