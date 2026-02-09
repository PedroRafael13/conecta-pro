"""Repositories do modulo Campo v3.0.0."""

# =============================================================================
# Legacy - Portaria Remota
# =============================================================================
from .access_log_repository import AccessLogRepository
from .checklist_repository import ChecklistRepository
from .equipment_status_repository import EquipmentStatusRepository
from .guardian_occurrence_repository import GuardianOccurrenceRepository
from .guardian_sync_repository import GuardianSyncRepository

# =============================================================================
# CAMPO - Ordens de Servico, Visitas, Checklists
# =============================================================================
from .ordem_servico_repository import OrdemServicoRepository
from .visita_repository import VisitaRepository

__all__ = [
    # Legacy
    "GuardianSyncRepository",
    "AccessLogRepository",
    "GuardianOccurrenceRepository",
    "EquipmentStatusRepository",
    # CAMPO
    "OrdemServicoRepository",
    "VisitaRepository",
    "ChecklistRepository",
]
