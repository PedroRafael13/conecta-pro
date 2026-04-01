"""Models do modulo Campo v3.0.0 - Servico de Campo."""

# Modelos Fisicos (Legacy - Portaria Remota)
from .access_log import AccessLog, AccessLogType

# Modelos CAMPO - Tecnicos
from .campo_tecnico import CampoTecnico

# Modelos CAMPO - Checklists
from .checklist import (
    CategoriaItem,
    ChecklistItem,
    ChecklistPreenchido,
    ChecklistResposta,
    ChecklistTemplate,
    TipoResposta,
    TipoServico,
)
from .equipment_status import EquipmentStatus, EquipmentStatusType

# Modelos CAMPO - Ordens de Servico
from .ordem_servico import (
    OrdemServico,
    OrigemOS,
    PrioridadeOS,
    StatusOS,
    TipoOS,
)

# Modelos CAMPO - Visitas
from .visita import (
    OrigemVisita,
    ResultadoVisita,
    StatusVisita,
    TipoResponsavel,
    TipoVisita,
    Visita,
)

__all__ = [
    # === Legacy (Portaria Remota) ===
    # AccessLog
    "AccessLog",
    "AccessLogType",
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
