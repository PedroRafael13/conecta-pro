"""Models do módulo Guardian Unified v3.0.0."""

# Modelos Físicos (Legacy)
from .access_log import AccessLog, AccessLogType
from .guardian_occurrence import (
    GuardianOccurrence,
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)
from .guardian_sync import GuardianSync, SyncDirection, SyncEntityType, SyncStatus
from .equipment_status import EquipmentStatus, EquipmentStatusType

# Modelos CAMPO
from .campo_tecnico import CampoTecnico

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
    # CAMPO
    "CampoTecnico",
]
