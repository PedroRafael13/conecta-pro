"""Models do módulo Remote Gatehouse."""

from .access_log import AccessLog, AccessLogType
from .guardian_occurrence import (
    GuardianOccurrence,
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)
from .guardian_sync import GuardianSync, SyncDirection, SyncEntityType, SyncStatus
from .equipment_status import EquipmentStatus, EquipmentStatusType

__all__ = [
    # GuardianSync
    "GuardianSync",
    "SyncStatus",
    "SyncDirection",
    "SyncEntityType",
    # AccessLog
    "AccessLog",
    "AccessLogType",
    # GuardianOccurrence
    "GuardianOccurrence",
    "OccurrenceType",
    "OccurrenceSeverity",
    "OccurrenceStatus",
    # EquipmentStatus
    "EquipmentStatus",
    "EquipmentStatusType",
]
