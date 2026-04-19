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

class InviteScope(str, Enum):
    ORGANIZATION = "ORGANIZATION"
    PROJECT = "PROJECT"

class IncidentLogType(str, Enum):
    COMMENT = "COMMENT"
    STATUS_CHANGED = "STATUS_CHANGED"
    ASSIGNEE_CHANGED = "ASSIGNEE_CHANGED"