"""Repositories do modulo Campo v3.0.0."""

# =============================================================================
# Legacy - Portaria Remota
# =============================================================================
from .access_log_repository import AccessLogRepository
from .checklist_repository import ChecklistRepository
from .equipment_status_repository import EquipmentStatusRepository

# =============================================================================
# CAMPO - Ordens de Servico, Visitas, Checklists
# =============================================================================
from .ordem_servico_repository import OrdemServicoRepository
from .visita_repository import VisitaRepository

__all__ = [
    # Legacy
    "AccessLogRepository",
    "EquipmentStatusRepository",
    # CAMPO
    "OrdemServicoRepository",
    "VisitaRepository",
    "ChecklistRepository",
]
