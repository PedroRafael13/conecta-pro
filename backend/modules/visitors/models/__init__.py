"""Models do módulo de Visitantes."""

from modules.visitors.models.visitor import (
    DocumentType,
    Visitor,
    VisitorStatus,
    VisitorType,
)
from modules.visitors.models.authorization import (
    AuthorizationStatus,
    AuthorizationType,
    RecurrenceType,
    VisitorAuthorization,
)
from modules.visitors.models.log import (
    AccessMethod,
    AccessPoint,
    AccessType,
    DenialReason,
    VisitorLog,
)
from modules.visitors.models.schedule import (
    SchedulePriority,
    ScheduleStatus,
    VisitorSchedule,
)

__all__ = [
    # Visitor
    "Visitor",
    "VisitorType",
    "VisitorStatus",
    "DocumentType",
    # Authorization
    "VisitorAuthorization",
    "AuthorizationType",
    "AuthorizationStatus",
    "RecurrenceType",
    # Log
    "VisitorLog",
    "AccessType",
    "AccessMethod",
    "AccessPoint",
    "DenialReason",
    # Schedule
    "VisitorSchedule",
    "ScheduleStatus",
    "SchedulePriority",
]
