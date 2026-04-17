from enum import Enum


class IncidentStatus(str, Enum):
    NEW = "NEW"
    PROBLEM_IS_BEING_SOLVED = "PROBLEM_IS_BEING_SOLVED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"


class IncidentPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"