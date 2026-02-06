"""Models do modulo Campo v3.0.0 - Servico de Campo."""

# Modelos Fisicos (Legacy - Portaria Remota)
from .access_log import AccessLog, AccessLogType
from .guardian_occurrence import (
    GuardianOccurrence,
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)
from .guardian_sync import GuardianSync, SyncDirection, SyncEntityType, SyncStatus
from .equipment_status import EquipmentStatus, EquipmentStatusType

# Modelos CAMPO - Tecnicos
from .campo_tecnico import CampoTecnico

# Modelos CAMPO - Ordens de Servico
from .ordem_servico import (
    OrdemServico,
    TipoOS,
    StatusOS,
    PrioridadeOS,
    OrigemOS,
)

# Modelos CAMPO - Visitas
from .visita import (
    Visita,
    TipoVisita,
    StatusVisita,
    ResultadoVisita,
    TipoResponsavel,
    OrigemVisita,
)

# Modelos CAMPO - Checklists
from .checklist import (
    ChecklistTemplate,
    ChecklistItem,
    ChecklistResposta,
    ChecklistPreenchido,
    TipoServico,
    TipoResposta,
    CategoriaItem,
)

__all__ = [
    # === Legacy (Portaria Remota) ===
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
    # === CAMPO - Tecnicos ===
    "CampoTecnico",
    # === CAMPO - Ordens de Servico ===
    "OrdemServico",
    "TipoOS",
    "StatusOS",
    "PrioridadeOS",
    "OrigemOS",
    # === CAMPO - Visitas ===
    "Visita",
    "TipoVisita",
    "StatusVisita",
    "ResultadoVisita",
    "TipoResponsavel",
    "OrigemVisita",
    # === CAMPO - Checklists ===
    "ChecklistTemplate",
    "ChecklistItem",
    "ChecklistResposta",
    "ChecklistPreenchido",
    "TipoServico",
    "TipoResposta",
    "CategoriaItem",
]
