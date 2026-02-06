"""Schemas do módulo Remote Gatehouse."""

from .access_log import (
    AccessLogCreate,
    AccessLogFilter,
    AccessLogListResponse,
    AccessLogResponse,
    AccessLogStats,
)
from .equipment_status import (
    EquipmentStatusCreate,
    EquipmentStatusFilter,
    EquipmentStatusListResponse,
    EquipmentStatusResponse,
    EquipmentStatusStats,
    EquipmentStatusUpdate,
)
from .guardian_occurrence import (
    GuardianOccurrenceAcknowledge,
    GuardianOccurrenceCreate,
    GuardianOccurrenceEscalate,
    GuardianOccurrenceFilter,
    GuardianOccurrenceListResponse,
    GuardianOccurrenceResolve,
    GuardianOccurrenceResponse,
    GuardianOccurrenceStats,
)
from .guardian_sync import (
    GuardianSyncCreate,
    GuardianSyncFilter,
    GuardianSyncListResponse,
    GuardianSyncResponse,
    GuardianSyncRetry,
    GuardianSyncStats,
)

__all__ = [
    # GuardianSync
    "GuardianSyncCreate",
    "GuardianSyncResponse",
    "GuardianSyncFilter",
    "GuardianSyncListResponse",
    "GuardianSyncRetry",
    "GuardianSyncStats",
    # AccessLog
    "AccessLogCreate",
    "AccessLogResponse",
    "AccessLogFilter",
    "AccessLogListResponse",
    "AccessLogStats",
    # GuardianOccurrence
    "GuardianOccurrenceCreate",
    "GuardianOccurrenceResponse",
    "GuardianOccurrenceFilter",
    "GuardianOccurrenceListResponse",
    "GuardianOccurrenceAcknowledge",
    "GuardianOccurrenceResolve",
    "GuardianOccurrenceEscalate",
    "GuardianOccurrenceStats",
    # EquipmentStatus
    "EquipmentStatusCreate",
    "EquipmentStatusUpdate",
    "EquipmentStatusResponse",
    "EquipmentStatusFilter",
    "EquipmentStatusListResponse",
    "EquipmentStatusStats",
]
